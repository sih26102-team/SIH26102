import requests
import json

BASE_URL = "http://localhost:8001"

# 1. Get Token
resp = requests.post(f"{BASE_URL}/auth/verify-otp", json={"username": "ministry.demo", "otp": "123456"})
token = resp.json().get("access_token")

# 2. Test Analytics Summary
headers = {"Authorization": f"Bearer {token}"}
summary_resp = requests.get(f"{BASE_URL}/analytics/summary", headers=headers)
print("Summary:", json.dumps(summary_resp.json(), indent=2))

# 3. Test Analytics Trends
trends_resp = requests.get(f"{BASE_URL}/analytics/trends", headers=headers)
print("Trends:", json.dumps(trends_resp.json(), indent=2))

# 4. Test District Stats
district_resp = requests.get(f"{BASE_URL}/analytics/districts", headers=headers)
print("Districts Sample:", json.dumps(district_resp.json()[:3], indent=2))
