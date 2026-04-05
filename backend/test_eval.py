import urllib.request
import json
import time

def test_url(target_url):
    url = 'http://127.0.0.1:8000/scan-url'
    data = json.dumps({'url': target_url}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    # Simple retry to avoid connection issues if the server takes a moment
    for _ in range(3):
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                print(f"URL: {target_url}")
                print(f"Risk Level: {res.get('risk_level')} | Threat Score: {res.get('threat_score'):.4f} | Action: {res.get('action')}")
                print("-" * 50)
                return
        except Exception as e:
            time.sleep(1)

test_url('https://google.com')
test_url('http://login-update-paypal-912.xyz/secure/verify.php')
test_url('https://secure-apple-auth.tk/login')
