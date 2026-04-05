import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_db_logging():
    print("1. Scanning a URL to generate a log entry...")
    scan_url = f"{BASE_URL}/scan-url"
    payload = json.dumps({"url": "http://db-test.com"}).encode("utf-8")
    req = urllib.request.Request(
        scan_url, 
        data=payload, 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req) as res:
            print(f"   Scan Status: {res.status}")
    except Exception as e:
        print(f"   Scan Failed: {e}")
        return

    print("2. Fetching logs to verify persistence...")
    logs_url = f"{BASE_URL}/logs"
    try:
        with urllib.request.urlopen(logs_url) as res:
            data = json.loads(res.read().decode("utf-8"))
            print(f"   Total Logs: {len(data)}")
            
            # Check if our recent scan is there
            found = False
            for log in data[:5]: # Check top 5
                print(f"   HEAD LOG: {log.get('url')} at {log.get('timestamp')}")
                if log.get("url") == "http://db-test.com":
                    found = True
                    print("   SUCCESS: Found recent scan in logs!")
                    print(f"   Log ID: {log.get('id')}")
                    break
            
            if not found:
                print("   FAILURE: Recent scan not found in logs.")
                
    except Exception as e:
        print(f"   Fetch Logs Failed: {e}")

if __name__ == "__main__":
    # Ensure server is running before running this
    test_db_logging()
