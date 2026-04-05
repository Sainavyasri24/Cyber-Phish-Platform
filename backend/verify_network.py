import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000/scan-url"

def scan(url):
    print(f"Scanning {url}...")
    try:
        payload = json.dumps({"url": url}).encode("utf-8")
        req = urllib.request.Request(
            BASE_URL, 
            data=payload, 
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as res:
            data = json.loads(res.read().decode("utf-8"))
            net = data.get("details", {}).get("network_features", {})
            print(f"  Risk Level: {data.get('risk_level')}")
            print(f"  Domain Age: {net.get('domain_age_days')} days")
            print(f"  DNS TTL: {net.get('dns_ttl')}")
            print("-" * 30)
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    scan("https://google.com")
    scan("https://example.com")
    scan("http://nonexistent-domain-12345.com")
