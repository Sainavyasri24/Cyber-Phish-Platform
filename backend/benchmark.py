import urllib.request
import json
import time

url = "http://127.0.0.1:8000/scan-url"
payload = {"url": "http://google.com"}
data = json.dumps(payload).encode('utf-8')
headers = {"Content-Type": "application/json"}

start = time.time()
try:
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req) as response:
        end = time.time()
        print(f"Status: {response.status}")
        print(f"Time taken: {end - start:.4f} seconds")
        print(response.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
