import urllib.request
import json

url = "http://127.0.0.1:8000/scan-url"
payload = {"url": "naployi.com/"}
data = json.dumps(payload).encode('utf-8')
headers = {"Content-Type": "application/json"}

try:
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"URL: {result['url']}")
        print(f"Action: {result['action']}")
        print(f"Risk: {result['risk_level']}")
except Exception as e:
    print(f"Error: {e}")
