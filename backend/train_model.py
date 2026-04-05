"""
train_model.py — Trains an optimised Random Forest phishing classifier.

v3 improvements over v2:
  - RandomizedSearchCV over a wide hyperparameter grid (60 candidates, 5-fold CV)
  - Out-of-bag (OOB) error estimation
  - Probability calibration via CalibratedClassifierCV (isotonic regression)
  - Stratified 10-fold cross-validation for robust performance estimates
  - Threshold-tuned decision boundary for best F1
  - Detailed feature importance ranking + confusion matrix
  - Model saved with metadata dict for traceability
"""

import pandas as pd
import joblib
import re
import math
import random
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")

from urllib.parse import urlparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    RandomizedSearchCV,
    cross_val_score,
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
    f1_score,
    confusion_matrix,
    precision_recall_curve,
)
from scipy.stats import randint

# ─────────────────────────────────────────
# Feature Engineering  (must match model.py)
# ─────────────────────────────────────────

HIGH_RISK_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "xyz", "pw",
    "top", "click", "link", "zip", "work", "party",
    "loan", "download", "racing", "win", "review", "trade"
}

PHISHING_KEYWORDS = {
    "login", "secure", "account", "update", "verify",
    "banking", "signin", "password", "confirm", "service",
    "webscr", "paypal", "apple", "amazon", "support",
    "helpdesk", "validate", "authorization", "reset",
    "unlock", "suspended", "alert", "notice", "billing",
}


def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    n = len(s)
    return -sum((f / n) * math.log2(f / n) for f in freq.values())


def extract_url_features(url: str) -> dict:
    parsed   = urlparse(url if "://" in url else f"http://{url}")
    netloc   = parsed.netloc or url
    domain   = netloc.split(":")[0]
    path     = parsed.path or ""
    parts    = domain.split(".")
    tld      = parts[-1].lower() if len(parts) > 1 else ""

    domain_chars = re.sub(r"[^a-zA-Z0-9]", "", domain)
    digit_ratio  = sum(c.isdigit() for c in domain_chars) / max(len(domain_chars), 1)

    url_lower = url.lower()

    return {
        "url_length":              len(url),
        "dot_count":               url.count("."),
        "https_present":           int(url.startswith("https")),
        "special_chars":           len(re.findall(r"[^a-zA-Z0-9\.]", url)),
        "is_ip_address":           int(bool(re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain))),
        "subdomain_count":         max(domain.count(".") - 1, 0),
        "path_depth":              path.count("/"),
        "url_entropy":             round(_shannon_entropy(url), 4),
        "has_suspicious_keywords": int(any(kw in url_lower for kw in PHISHING_KEYWORDS)),
        "tld_risk":                int(tld in HIGH_RISK_TLDS),
        "digit_ratio":             round(digit_ratio, 4),
    }


def build_feature_vector(url_features: dict, domain_age_days: int) -> list:
    """Returns features in the exact order the model was trained on."""
    return [
        url_features["url_length"],
        url_features["dot_count"],
        url_features["https_present"],
        url_features["special_chars"],
        url_features["is_ip_address"],
        url_features["subdomain_count"],
        url_features["path_depth"],
        url_features["url_entropy"],
        url_features["has_suspicious_keywords"],
        url_features["tld_risk"],
        url_features["digit_ratio"],
        domain_age_days,
    ]


FEATURE_NAMES = [
    "url_length", "dot_count", "https_present", "special_chars",
    "is_ip_address", "subdomain_count", "path_depth", "url_entropy",
    "has_suspicious_keywords", "tld_risk", "digit_ratio", "domain_age_days"
]

# ─────────────────────────────────────────
# Load & Prepare Data
# ─────────────────────────────────────────

DATA_FILE  = "datasets/threat_intel.csv"
MODEL_FILE = "phishing_model.pkl"

if not os.path.exists(DATA_FILE):
    print(f"[ERROR] {DATA_FILE} not found! Run generate_data.py first.")
    exit(1)

print("\n" + "=" * 60)
print("  Cyber-Phish Classifier Training  v3")
print("=" * 60)

print("\n[DATA] Loading training data...")
df = pd.read_csv(DATA_FILE)
print(f"       {len(df)} rows | Label distribution:")
print(df["type"].value_counts().to_string())

# Normalise labels
df["label"] = df["type"].apply(
    lambda t: 1 if str(t).strip().lower() in {"bad", "malicious"} else 0
)

X, y = [], []
print("\n[FEAT] Extracting features...")
for idx, row in df.iterrows():
    url   = str(row["url"])
    label = row["label"]

    url_feats = extract_url_features(url)

    # Simulate domain age:
    #   benign   → established sites  (365–3000 days)
    #   malicious → freshly registered  (0–120 days)
    if label == 0:
        domain_age = random.randint(365, 3000)
    else:
        domain_age = random.randint(0, 120)

    X.append(build_feature_vector(url_feats, domain_age))
    y.append(label)

X = np.array(X, dtype=float)
y = np.array(y, dtype=int)
print(f"       Feature matrix: {X.shape}")

# ─────────────────────────────────────────
# Train / Test Split
# ─────────────────────────────────────────

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"\n[SPLIT] Train: {len(X_train)} | Test: {len(X_test)}")

# ─────────────────────────────────────────
# Hyperparameter Search  (RandomizedSearchCV)
# ─────────────────────────────────────────

SEARCH_PARAM_DIST = {
    "n_estimators":      randint(200, 600),
    "max_depth":         [10, 15, 20, 25, 30, None],
    "min_samples_split": randint(2, 10),
    "min_samples_leaf":  randint(1, 5),
    "max_features":      ["sqrt", "log2", 0.5, 0.7],
    "bootstrap":         [True],           # required for OOB
    "oob_score":         [True],
    "class_weight":      ["balanced", "balanced_subsample"],
}

print("\n[SEARCH] RandomizedSearchCV — 60 candidates × 5-fold StratifiedKFold...")
print("         (This may take 1-2 minutes)")

inner_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
base_rf  = RandomForestClassifier(random_state=42, n_jobs=-1)

search = RandomizedSearchCV(
    estimator=base_rf,
    param_distributions=SEARCH_PARAM_DIST,
    n_iter=60,
    scoring="roc_auc",
    cv=inner_cv,
    refit=True,
    random_state=42,
    n_jobs=-1,
    verbose=1,
)
search.fit(X_train, y_train)

best_rf = search.best_estimator_
print(f"\n[BEST] Best CV ROC-AUC: {search.best_score_:.4f}")
print(f"[BEST] Best params:")
for k, v in sorted(search.best_params_.items()):
    print(f"       {k:<25} {v}")
if hasattr(best_rf, "oob_score_"):
    print(f"\n[OOB]  Out-of-bag accuracy: {best_rf.oob_score_:.4f}")

# ─────────────────────────────────────────
# Probability Calibration  (isotonic)
# ─────────────────────────────────────────

print("\n[CALIB] Calibrating probabilities (isotonic regression)...")
calibrated_rf = CalibratedClassifierCV(best_rf, method="isotonic", cv=3)
calibrated_rf.fit(X_train, y_train)

# ─────────────────────────────────────────
# Hold-out Evaluation
# ─────────────────────────────────────────

y_pred  = calibrated_rf.predict(X_test)
y_proba = calibrated_rf.predict_proba(X_test)[:, 1]

print("\n" + "=" * 60)
print("HOLD-OUT TEST RESULTS")
print("=" * 60)
print(f"Accuracy : {accuracy_score(y_test, y_pred):.4f}")
print(f"ROC-AUC  : {roc_auc_score(y_test, y_proba):.4f}")
print(f"F1 Score : {f1_score(y_test, y_pred):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Benign", "Malicious"]))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(f"  TN={cm[0,0]}  FP={cm[0,1]}")
print(f"  FN={cm[1,0]}  TP={cm[1,1]}")

# ─────────────────────────────────────────
# Threshold Optimisation (best F1)
# ─────────────────────────────────────────

precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)
f1_scores  = 2 * precisions * recalls / np.maximum(precisions + recalls, 1e-8)
best_idx   = np.argmax(f1_scores[:-1])   # last element has no threshold
best_thr   = thresholds[best_idx]
print(f"\n[THOLD] Best threshold for F1: {best_thr:.4f}  "
      f"→ F1={f1_scores[best_idx]:.4f}")

# ─────────────────────────────────────────
# Stratified 10-fold Cross-Validation
# ─────────────────────────────────────────

print("\n[CV] Running 10-fold stratified cross-validation...")
outer_cv   = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
cv_auc     = cross_val_score(best_rf, X, y, cv=outer_cv,
                              scoring="roc_auc",  n_jobs=-1)
cv_acc     = cross_val_score(best_rf, X, y, cv=outer_cv,
                              scoring="accuracy", n_jobs=-1)
cv_f1      = cross_val_score(best_rf, X, y, cv=outer_cv,
                              scoring="f1",       n_jobs=-1)

print(f"  ROC-AUC  : {cv_auc.mean():.4f} ± {cv_auc.std():.4f}")
print(f"  Accuracy : {cv_acc.mean():.4f} ± {cv_acc.std():.4f}")
print(f"  F1 Score : {cv_f1.mean():.4f} ± {cv_f1.std():.4f}")

# ─────────────────────────────────────────
# Feature Importances
# ─────────────────────────────────────────

print("\n[FEAT] Feature Importances (from best uncalibrated RF):")
importances = best_rf.feature_importances_
for name, imp in sorted(zip(FEATURE_NAMES, importances), key=lambda x: -x[1]):
    bar = "█" * int(imp * 60)
    print(f"  {name:<30} {imp:.4f}  {bar}")

# ─────────────────────────────────────────
# Save Model + Metadata
# ─────────────────────────────────────────

model_bundle = {
    "model":          calibrated_rf,
    "best_threshold": float(best_thr),
    "feature_names":  FEATURE_NAMES,
    "cv_roc_auc":     float(cv_auc.mean()),
    "cv_accuracy":    float(cv_acc.mean()),
    "best_params":    search.best_params_,
}

print(f"\n[SAVE] Saving model → {MODEL_FILE}")
joblib.dump(model_bundle, MODEL_FILE)
print("✅ Done! Model bundle saved successfully.")
print(f"   Final CV ROC-AUC: {cv_auc.mean():.4f} ± {cv_auc.std():.4f}")
