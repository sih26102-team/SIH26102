import requests
import json
from jose import jwt

BASE_URL = "http://localhost:8001/auth"
SECRET = "SIH2026_SUPER_SECRET_KEY"

users = [
    {"username": "ministry.demo", "expected_role": "MINISTRY"},
    {"username": "state.demo", "expected_role": "STATE_AUTHORITY"},
    {"username": "district.demo", "expected_role": "DISTRICT_AUTHORITY"},
    {"username": "officer.demo", "expected_role": "INSPECTION_OFFICER"}
]

print("--- VERIFYING PHASE 1 AUTHENTICATION PATHS ---")

for u in users:
    print(f"\nTesting login path for: {u['username']}")
    
    # 1. Login (Challenge OTP)
    resp = requests.post(f"{BASE_URL}/login", json={"username": u["username"], "password": "Password123"})
    if resp.status_code == 200:
        print(f"  [+] Login challenge successful. OTP required: {resp.json().get('requires_otp')}")
    else:
        print(f"  [-] Login failed: {resp.text}")
        continue
        
    # 2. Verify OTP (Simulate 123456)
    resp = requests.post(f"{BASE_URL}/verify-otp", json={"username": u["username"], "otp": "123456"})
    if resp.status_code == 200:
        data = resp.json()
        token = data.get("access_token")
        print(f"  [+] OTP Verified. JWT received.")
        
        # 3. Role detection & Decoding JWT
        decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
        role = decoded.get("role")
        print(f"  [+] Role detected from JWT: {role}")
        
        if role == u["expected_role"]:
            print(f"  [+] SUCCESS: Path correctly routes to {role} dashboard placeholder.")
        else:
            print(f"  [-] FAILURE: Role mismatch.")
    else:
        print(f"  [-] OTP verification failed: {resp.text}")

print("\n--- PHASE 1 VERIFICATION COMPLETE ---")
