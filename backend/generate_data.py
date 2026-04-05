"""
generate_data.py — Generates high-quality synthetic phishing / benign URL data.

v3 improvements:
  - 2 000 samples per class (was 600) for a richer training set
  - 12 distinct malicious attack patterns (was 8)
  - New patterns: punycode spoof, data-URI, redirect chain, combo attack
  - Benign set covers more realistic traffic patterns (CDN, API, deep paths)
  - Strict deduplication + balanced final class distribution
  - Output backed up before overwrite
"""

import pandas as pd
import random
import string
import os

NUM_BENIGN    = 2000
NUM_MALICIOUS = 2000
SOURCE_FILE   = "datasets/threat_intel.csv"

# ─── Resources ───────────────────────────────────────────────────────────────

COMMON_DOMAINS = [
    "google.com", "facebook.com", "amazon.com", "apple.com", "microsoft.com",
    "netflix.com", "wikipedia.org", "yahoo.com", "twitter.com", "linkedin.com",
    "instagram.com", "adobe.com", "github.com", "paypal.com", "ebay.com",
    "chase.com", "wellsfargo.com", "bankofamerica.com", "dropbox.com", "icloud.com",
    "spotify.com", "salesforce.com", "zoom.us", "slack.com", "notion.so",
    "cloudflare.com", "stripe.com", "twilio.com", "shopify.com", "airbnb.com",
    "reddit.com", "stackoverflow.com", "medium.com", "quora.com", "yelp.com",
]

SAFE_TLDS       = ["com", "org", "net", "io", "co", "edu", "gov", "uk", "de", "ca"]
HIGH_RISK_TLDS  = [
    "tk", "ml", "ga", "cf", "xyz", "pw", "top", "click",
    "link", "work", "loan", "win", "review", "download",
    "racing", "party", "trade", "zip", "gq",
]
PHISHING_KEYWORDS = [
    "login", "secure", "account", "update", "verify",
    "banking", "signin", "password", "confirm", "support",
    "helpdesk", "validate", "webscr", "authorization", "reset",
    "unlock", "suspended", "alert", "notice", "billing",
]
BRANDS = ["apple", "paypal", "amazon", "google", "microsoft",
          "netflix", "bank", "instagram", "facebook", "ebay"]

BENIGN_SUBS    = ["www", "mail", "docs", "blog", "shop", "support", "api",
                  "cdn", "static", "assets", "media", "help", "dev"]
BENIGN_CATS    = ["products", "articles", "docs", "posts", "pages", "blog",
                  "news", "about", "pricing", "careers", "legal", "help",
                  "api/v1", "api/v2", "assets", "downloads", "releases"]

def rand_str(n: int, chars=string.ascii_lowercase) -> str:
    return "".join(random.choices(chars, k=n))

def rand_alnum(n: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


# ─── Benign URL Generator ────────────────────────────────────────────────────

def generate_benign_url() -> str:
    domain   = random.choice(COMMON_DOMAINS)
    protocol = "https"          # benign sites nearly always use HTTPS

    r = random.random()

    if r < 0.20:                # simple root URL
        return f"{protocol}://{domain}"

    elif r < 0.35:              # short path
        path = rand_str(random.randint(4, 10))
        return f"{protocol}://{domain}/{path}"

    elif r < 0.48:              # search / query string
        q = rand_str(random.randint(3, 10))
        return f"{protocol}://{domain}/search?q={q}"

    elif r < 0.60:              # category + slug
        cat  = random.choice(BENIGN_CATS)
        slug = rand_str(random.randint(5, 15))
        return f"{protocol}://{domain}/{cat}/{slug}"

    elif r < 0.70:              # subdomain
        sub = random.choice(BENIGN_SUBS)
        return f"{protocol}://{sub}.{domain}"

    elif r < 0.80:              # deep path (resource-style)
        depth  = random.randint(2, 4)
        parts  = "/".join(rand_str(random.randint(4, 8)) for _ in range(depth))
        return f"{protocol}://{domain}/{parts}"

    elif r < 0.88:              # versioned API endpoint
        ver    = f"v{random.randint(1, 4)}"
        res    = random.choice(["users", "products", "orders", "events", "reports"])
        rid    = rand_alnum(8)
        return f"{protocol}://api.{domain}/{ver}/{res}/{rid}"

    elif r < 0.94:              # CDN / asset URL
        asset  = random.choice(["js", "css", "png", "woff2", "svg"])
        hash_  = rand_alnum(16)
        return f"{protocol}://cdn.{domain}/static/{hash_}.{asset}"

    else:                       # paginated listing
        cat  = random.choice(["products", "blog", "articles"])
        page = random.randint(1, 50)
        return f"{protocol}://{domain}/{cat}?page={page}&limit=20"


# ─── Malicious URL Generator ─────────────────────────────────────────────────

def generate_malicious_url() -> str:
    protocol = "http" if random.random() < 0.65 else "https"

    attack_type = random.choice([
        "ip_url",           # bare IP address
        "long_random",      # very long random domain
        "keyword_spoof",    # phishing keywords + brand
        "brand_subdomain",  # many subdomain levels
        "high_risk_tld",    # free / disposable TLD
        "encoded_chars",    # percent-encoding / special chars
        "typosquat",        # look-alike brand domain
        "suspicious_path",  # normal domain, evil path
        "punycode_spoof",   # unicode/xn-- prefix tricks
        "redirect_chain",   # open-redirect style chain
        "data_exfil",       # long base64-like query param
        "combo_attack",     # combine multiple signals
    ])

    if attack_type == "ip_url":
        ip    = ".".join(str(random.randint(1, 254)) for _ in range(4))
        paths = ["/admin", "/login", "/wp-admin", "/wp-login.php",
                 f"/page{random.randint(1, 99)}", "/cgi-bin/login.cgi"]
        return f"{protocol}://{ip}{random.choice(paths)}"

    elif attack_type == "long_random":
        domain = rand_str(random.randint(28, 60))
        tld    = random.choice(SAFE_TLDS + HIGH_RISK_TLDS)
        return f"{protocol}://{domain}.{tld}"

    elif attack_type == "keyword_spoof":
        kw     = random.choice(PHISHING_KEYWORDS)
        brand  = random.choice(BRANDS)
        suffix = random.randint(100, 9999)
        tld    = random.choice(SAFE_TLDS + HIGH_RISK_TLDS)
        path   = random.choice(["/login.php", "/account/verify",
                                 "/secure/update", "/signin.html",
                                 "/auth/reset-password"])
        return f"{protocol}://{kw}-{brand}-{suffix}.{tld}{path}"

    elif attack_type == "brand_subdomain":
        # e.g. xyz.abc.secure.google.com.evil.tk
        levels = ".".join(rand_str(random.randint(3, 6))
                          for _ in range(random.randint(3, 5)))
        brand  = random.choice(BRANDS)
        tld    = random.choice(HIGH_RISK_TLDS)
        return f"{protocol}://{levels}.{brand}.{tld}"

    elif attack_type == "high_risk_tld":
        domain = rand_str(random.randint(6, 20))
        tld    = random.choice(HIGH_RISK_TLDS)
        path   = random.choice(["", "/login", "/verify", "/update",
                                  "/account/confirm", "/wp-login.php"])
        return f"{protocol}://{domain}.{tld}{path}"

    elif attack_type == "encoded_chars":
        brand  = random.choice(BRANDS)
        filler = "".join(random.choices(
            string.ascii_letters + string.digits + "@%-_=~!", k=random.randint(10, 25)
        ))
        tld    = random.choice(SAFE_TLDS)
        return f"{protocol}://{brand}-{filler}.{tld}/login"

    elif attack_type == "typosquat":
        brand = random.choice(BRANDS)
        typos = [
            brand.replace(brand[1], brand[1] * 2),          # gooogle
            brand + brand[-1],                               # amazonn
            brand.replace("o", "0").replace("i", "1"),      # g00gle
            brand[:-1] + "q",                               # googq
            brand + "-" + rand_str(3),                      # google-xyz
            brand.replace("a", "à") if "a" in brand else brand + "s",
        ]
        fake = random.choice(typos)
        tld  = random.choice(SAFE_TLDS + HIGH_RISK_TLDS)
        return f"{protocol}://{fake}.{tld}"

    elif attack_type == "suspicious_path":
        domain  = rand_str(random.randint(6, 14))
        tld     = random.choice(SAFE_TLDS + HIGH_RISK_TLDS)
        segment = random.choice(PHISHING_KEYWORDS)
        ending  = random.choice([
            "confirm.php", "signin.html", "update.aspx",
            "credential-check.php", "auth.cgi"
        ])
        return f"{protocol}://{domain}.{tld}/user/{segment}/{ending}"

    elif attack_type == "punycode_spoof":
        # xn-- prefix to mimic international look-alike domains
        brand  = random.choice(BRANDS)
        mangled = "xn--" + brand + rand_alnum(4)
        tld    = random.choice(SAFE_TLDS)
        return f"{protocol}://{mangled}.{tld}/login"

    elif attack_type == "redirect_chain":
        # Abuse open-redirect pattern: legit-looking URL redirects to evil dest
        redir_host = rand_str(random.randint(6, 14))
        tld        = random.choice(HIGH_RISK_TLDS)
        dest       = rand_str(random.randint(8, 20)) + "." + random.choice(HIGH_RISK_TLDS)
        return f"{protocol}://{redir_host}.{tld}/redirect?url=http://{dest}/phish"

    elif attack_type == "data_exfil":
        # Very long base64-like query parameter (exfiltration beacon)
        domain  = rand_str(random.randint(6, 14))
        tld     = random.choice(HIGH_RISK_TLDS)
        payload = rand_alnum(random.randint(60, 120))
        return f"{protocol}://{domain}.{tld}/track?data={payload}"

    else:   # combo_attack — multiple signals at once
        kw     = random.choice(PHISHING_KEYWORDS)
        brand  = random.choice(BRANDS)
        tld    = random.choice(HIGH_RISK_TLDS)
        levels = ".".join(rand_str(3) for _ in range(random.randint(2, 4)))
        path   = f"/{kw}/confirm-{rand_alnum(8)}.php"
        return f"{protocol}://{levels}.{brand}-{kw}.{tld}{path}"


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Cyber-Phish: Training Data Generator  v3")
    print("=" * 60)

    # Load existing data (discard if missing required 'type' column)
    try:
        df_existing = pd.read_csv(SOURCE_FILE)
        if "type" not in df_existing.columns:
            raise ValueError("Missing 'type' column — discarding unlabelled data.")
        print(f"\n[INFO] Loaded {len(df_existing)} existing rows.")
        print(f"       Distribution:\n{df_existing['type'].value_counts().to_string()}")
    except Exception as exc:
        df_existing = pd.DataFrame(columns=["url", "type"])
        print(f"\n[INFO] Starting fresh ({exc})")

    # Generate new samples
    print(f"\n[GEN]  Generating {NUM_BENIGN} benign + {NUM_MALICIOUS} malicious URLs...")
    new_rows = []
    for _ in range(NUM_BENIGN):
        new_rows.append({"url": generate_benign_url(),    "type": "good"})
    for _ in range(NUM_MALICIOUS):
        new_rows.append({"url": generate_malicious_url(), "type": "bad"})

    df_new   = pd.DataFrame(new_rows)
    df_final = pd.concat([df_existing, df_new], ignore_index=True)

    # Deduplicate, then balance classes to the minority count
    df_final  = df_final.drop_duplicates(subset="url")
    min_class = df_final["type"].value_counts().min()
    # Pandas 2.x-safe balancing: sample each class independently then concat
    parts = [
        grp.sample(min(len(grp), min_class), random_state=42)
        for _, grp in df_final.groupby("type")
    ]
    df_balanced = (
        pd.concat(parts, ignore_index=True)
        .sample(frac=1, random_state=42)
        .reset_index(drop=True)
    )

    # Backup original before overwriting
    if os.path.exists(SOURCE_FILE):
        backup = SOURCE_FILE + ".bak"
        df_existing.to_csv(backup, index=False)
        print(f"[BAK]  Original backed up → {backup}")

    os.makedirs(os.path.dirname(SOURCE_FILE), exist_ok=True)
    df_balanced.to_csv(SOURCE_FILE, index=False)

    print(f"\n[DONE] Saved {len(df_balanced)} balanced rows to {SOURCE_FILE}")
    print(f"       Final class distribution:\n{df_balanced['type'].value_counts().to_string()}")
    print()


if __name__ == "__main__":
    main()
