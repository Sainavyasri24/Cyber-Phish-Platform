import urllib.request
import json

url = "http://127.0.0.1:8000/scan-url"
payload = {"url": "https://example.com"}
data = json.dumps(payload).encode('utf-8')
headers = {"Content-Type": "application/json"}

req = urllib.request.Request(url, data=data, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        data = json.loads(response.read().decode('utf-8'))
        print(f"Risk Level: {data.get('risk_level')}")
        print(f"Action: {data.get('action')}")
        print(f"Details Present: {'details' in data}")
        if 'details' in data:
            print(f"Network Features Present: {'network_features' in data['details']}")
except Exception as e:
    print(f"Error: {e}")
