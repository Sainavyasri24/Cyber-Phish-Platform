import urllib.request
import urllib.parse
import json
import ssl

BASE_URL = "http://127.0.0.1:8000"

def test_auth_flow():
    print("--- Testing Authentication Flow ---")
    
    # 1. Register
    print("\n1. Registering new user 'testuser'...")
    register_url = f"{BASE_URL}/register"
    data = json.dumps({"username": "testuser", "password": "password123"}).encode("utf-8")
    req = urllib.request.Request(
        register_url, 
        data=data, 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req) as res:
            print(f"   Register Status: {res.status}")
            print(f"   Response: {res.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        if e.code == 400: # Already registered
             print("   User already exists (expected if re-running).")
        else:
             print(f"   Register Failed: {e}")
             return

    # 2. Login (Get Token)
    print("\n2. Logging in to get access token...")
    token_url = f"{BASE_URL}/token"
    # OAuth2PasswordRequestForm expects form data, not JSON
    data = urllib.parse.urlencode({"username": "testuser", "password": "password123"}).encode("utf-8")
    req = urllib.request.Request(
        token_url, 
        data=data, 
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    token = None
    try:
         with urllib.request.urlopen(req) as res:
            body = json.loads(res.read().decode("utf-8"))
            token = body.get("access_token")
            print(f"   Login Success! Token: {token[:20]}...")
    except Exception as e:
        print(f"   Login Failed: {e}")
        return

    # 3. Access Protected Route (Logs)
    print("\n3. Accessing /logs with token...")
    logs_url = f"{BASE_URL}/logs"
    req = urllib.request.Request(
        logs_url, 
        headers={"Authorization": f"Bearer {token}"}
    )
    
    try:
        with urllib.request.urlopen(req) as res:
             print(f"   Access Granted! Status: {res.status}")
             logs = json.loads(res.read().decode("utf-8"))
             print(f"   Logs retrieved: {len(logs)}")
    except Exception as e:
        print(f"   Access Failed: {e}")

    # 4. Access Protected Route (No Token)
    print("\n4. Accessing /logs WITHOUT token (Expect Failure)...")
    req = urllib.request.Request(logs_url)
    try:
        with urllib.request.urlopen(req) as res:
             print(f"   UNEXPECTED SUCCESS: {res.status}")
    except urllib.error.HTTPError as e:
        print(f"   Success! Access Denied as expected: {e.code} {e.reason}")

if __name__ == "__main__":
    test_auth_flow()
