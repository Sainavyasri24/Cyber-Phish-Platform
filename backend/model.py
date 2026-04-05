import random
import re
import math
from datetime import datetime
from urllib.parse import urlparse

# ─────────────────────────────────────────
# Feature Engineering Helpers
# ─────────────────────────────────────────

# TLDs associated with higher phishing risk
HIGH_RISK_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "xyz", "pw",
    "top", "click", "link", "zip", "work", "party",
    "loan", "download", "racing", "win", "review", "trade"
}

# Keywords commonly abused in phishing URLs
PHISHING_KEYWORDS = {
    "login", "secure", "account", "update", "verify",
    "banking", "signin", "password", "confirm", "service",
    "webscr", "paypal", "apple", "amazon", "support",
    "helpdesk", "validate", "authorization"
}

def _shannon_entropy(s: str) -> float:
    """Shannon entropy of a string. High entropy → likely gibberish/encoded."""
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    n = len(s)
    return -sum((f / n) * math.log2(f / n) for f in freq.values())


# ─────────────────────────────────────────
# Feature Extraction  (12 features)
# ─────────────────────────────────────────

# FEATURE ORDER (must match train_model.py exactly):
#  0  url_length
#  1  dot_count
#  2  https_present
#  3  special_chars
#  4  is_ip_address
#  5  subdomain_count
#  6  path_depth
#  7  url_entropy
#  8  has_suspicious_keywords
#  9  tld_risk
# 10  digit_ratio
# 11  domain_age_days   ← from network layer

FEATURE_NAMES = [
    "url_length", "dot_count", "https_present", "special_chars",
    "is_ip_address", "subdomain_count", "path_depth", "url_entropy",
    "has_suspicious_keywords", "tld_risk", "digit_ratio", "domain_age_days"
]


def extract_url_features(url: str) -> dict:
    """Extracts 11 URL-only heuristic features from a URL string."""
    parsed = urlparse(url if "://" in url else f"http://{url}")
    netloc = parsed.netloc or url
    domain = netloc.split(":")[0]          # strip port
    path   = parsed.path or ""

    # TLD extraction
    parts = domain.split(".")
    tld   = parts[-1].lower() if len(parts) > 1 else ""

    # Digit ratio in domain
    domain_chars = re.sub(r"[^a-zA-Z0-9]", "", domain)
    digit_ratio  = sum(c.isdigit() for c in domain_chars) / max(len(domain_chars), 1)

    # Subdomain count (dots before registered domain = dots - 1 for most)
    subdomain_count = max(domain.count(".") - 1, 0)

    # Suspicious keywords anywhere in the URL
    url_lower  = url.lower()
    has_keywords = int(any(kw in url_lower for kw in PHISHING_KEYWORDS))

    return {
        "url_length":             len(url),
        "dot_count":              url.count("."),
        "https_present":          int(url.startswith("https")),
        "special_chars":          len(re.findall(r"[^a-zA-Z0-9\.]", url)),
        "is_ip_address":          int(bool(re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain))),
        "subdomain_count":        subdomain_count,
        "path_depth":             path.count("/"),
        "url_entropy":            round(_shannon_entropy(url), 4),
        "has_suspicious_keywords": has_keywords,
        "tld_risk":               int(tld in HIGH_RISK_TLDS),
        "digit_ratio":            round(digit_ratio, 4),
    }


# ─────────────────────────────────────────
# Network Feature Extraction
# ─────────────────────────────────────────

import whois
import dns.resolver

def get_domain_age(domain: str) -> int:
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date:
            if creation_date.tzinfo is not None:
                creation_date = creation_date.replace(tzinfo=None)
            return (datetime.now() - creation_date).days
    except Exception:
        pass
    return -1


def get_dns_info(domain: str) -> dict:
    try:
        answers = dns.resolver.resolve(domain, "A")
        return {"ttl": answers.rrset.ttl, "ips": [r.to_text() for r in answers]}
    except Exception:
        pass
    return {"ttl": -1, "ips": []}


def extract_network_features(url: str = "") -> dict:
    """
    Extracts real network features (WHOIS + DNS).
    Falls back to safe defaults when lookups fail.
    """
    if not url:
        return {
            "dns_ttl":         300,
            "asn_risk":        0,
            "packet_rate":     random.uniform(10, 1000),
            "flow_duration":   random.uniform(0.1, 60),
            "domain_age_days": 1000,
        }

    try:
        parsed = urlparse(url if "://" in url else f"http://{url}")
        domain = parsed.netloc.split(":")[0] or url

        age      = get_domain_age(domain)
        dns_data = get_dns_info(domain)

        return {
            "dns_ttl":         dns_data["ttl"] if dns_data["ttl"] != -1 else 300,
            "asn_risk":        0,   # Placeholder — ASN lookup not yet wired
            "packet_rate":     random.uniform(10, 1000),   # Still simulated
            "flow_duration":   random.uniform(0.1, 60),    # Still simulated
            "domain_age_days": age if age != -1 else 0,
        }
    except Exception as e:
        print(f"[WARN] Network extraction error: {e}")
        return {
            "dns_ttl":         300,
            "asn_risk":        0,
            "packet_rate":     0,
            "flow_duration":   0,
            "domain_age_days": 0,
        }


# ─────────────────────────────────────────
# Load ML Model
# ─────────────────────────────────────────

import joblib
import os
import numpy as np

MODEL_PATH     = os.path.join(os.path.dirname(__file__), "phishing_model.pkl")
rf_model       = None
_BEST_THRESHOLD = 0.5   # default; overridden by bundle metadata if present

if os.path.exists(MODEL_PATH):
    try:
        _bundle = joblib.load(MODEL_PATH)
        # Support both legacy bare model and new bundle dict
        if isinstance(_bundle, dict) and "model" in _bundle:
            rf_model        = _bundle["model"]
            _BEST_THRESHOLD = _bundle.get("best_threshold", 0.5)
            _cv_auc         = _bundle.get("cv_roc_auc", None)
            _auc_str        = f" | CV ROC-AUC={_cv_auc:.4f}" if _cv_auc else ""
            print(f"[OK] ML model bundle loaded from {MODEL_PATH}{_auc_str}")
        else:
            rf_model = _bundle
            print(f"[OK] ML model (legacy) loaded from {MODEL_PATH}")
    except Exception as e:
        print(f"[WARN] Failed to load ML model: {e}")
else:
    print("[WARN] No ML model found — using heuristics only.")


# ─────────────────────────────────────────
# Threat Score Computation
# ─────────────────────────────────────────

def compute_threat_score(url_features: dict, network_features: dict) -> float:
    """
    Computes a 0–1 threat score.
    Uses the RF model (12 features) when available, else weighted heuristics.
    """
    if rf_model:
        try:
            domain_age = network_features.get("domain_age_days", 0)
            feature_vector = [
                url_features.get("url_length",              0),
                url_features.get("dot_count",               0),
                url_features.get("https_present",           0),
                url_features.get("special_chars",           0),
                url_features.get("is_ip_address",           0),
                url_features.get("subdomain_count",         0),
                url_features.get("path_depth",              0),
                url_features.get("url_entropy",             0.0),
                url_features.get("has_suspicious_keywords", 0),
                url_features.get("tld_risk",                0),
                url_features.get("digit_ratio",             0.0),
                domain_age
            ]
            # Use calibrated probabilities from the new bundle model
            prob = rf_model.predict_proba([feature_vector])[0][1]
            return float(prob)
        except Exception as e:
            print(f"[WARN] ML prediction error: {e}. Falling back to heuristics.")

    # ── Heuristic fallback ──
    score = 0.0
    if url_features.get("is_ip_address"):             score += 0.25
    if url_features.get("url_length", 0) > 75:        score += 0.15
    if url_features.get("special_chars", 0) > 5:      score += 0.10
    if not url_features.get("https_present"):          score += 0.10
    if url_features.get("tld_risk"):                   score += 0.15
    if url_features.get("has_suspicious_keywords"):    score += 0.10
    if url_features.get("subdomain_count", 0) > 2:    score += 0.10
    if url_features.get("url_entropy", 0) > 4.5:      score += 0.10
    if network_features.get("domain_age_days", 999) < 30: score += 0.20
    if network_features.get("asn_risk"):               score += 0.20
    return min(score, 1.0)


# ─────────────────────────────────────────
# Risk Level & Adaptive Response
# ─────────────────────────────────────────

def risk_level(score: float) -> str:
    if score >= 0.70:
        return "High"
    elif score >= 0.40:
        return "Medium"
    else:
        return "Low"


def adaptive_response(risk: str) -> str:
    if risk == "High":
        return "BLOCKED | Alert sent to SIEM"
    elif risk == "Medium":
        return "WARNING issued to user"
    else:
        return "ACCESS ALLOWED"