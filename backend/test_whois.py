import whois
from datetime import datetime

print("Starting WHOIS lookup for google.com...")
start = datetime.now()
try:
    w = whois.whois("google.com")
    print("WHOIS lookup successful")
    print(f"Creation Date: {w.creation_date}")
except Exception as e:
    print(f"WHOIS lookup failed: {e}")
print(f"Time taken: {(datetime.now() - start).total_seconds()}s")
