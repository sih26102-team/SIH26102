import requests
import json

BASE_URL = "http://localhost:8001"

# 1. Get Token
resp = requests.post(f"{BASE_URL}/auth/verify-otp", json={"username": "ministry.demo", "otp": "123456"})
token = resp.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# 2. Trigger Risk Engine
print("Triggering /risk/analyze...")
analyze_resp = requests.post(f"{BASE_URL}/risk/analyze", headers=headers)
print("Analyze Response:", analyze_resp.json())

# 3. Fetch Controlled Project
print("\nFetching Demo Anomaly PRJ-2026-1042...")
proj_resp = requests.get(f"{BASE_URL}/risk/projects/PRJ-2026-1042", headers=headers)
print("PRJ-2026-1042 Risk Data:", json.dumps(proj_resp.json(), indent=2))
