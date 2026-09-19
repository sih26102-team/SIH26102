import requests
import json

BASE_URL = "http://localhost:8001"

# 1. Login as District Authority
resp = requests.post(f"{BASE_URL}/auth/verify-otp", json={"username": "district.demo", "otp": "123456"})
token = resp.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

target_case = 2 # From our previous test

# 2. Fetch the case details to ensure it has all info
print("Fetching Case for Review...")
case_resp = requests.get(f"{BASE_URL}/cases/{target_case}", headers=headers).json()
print("Case Status:", case_resp["case"]["status"])
if case_resp["inspections"]:
    print("Found Inspections:", len(case_resp["inspections"]))
    print("Checklist Responses:", case_resp["inspections"][0]["checklist_responses"])
else:
    print("No inspections found.")

# 3. Post a Review Decision
print("\nSubmitting Review Decision (VERIFIED)...")
review_data = {
    "status": "VERIFIED",
    "resolution": "All physical records matched. Minor deviations acceptable. Issue resolved."
}
review_resp = requests.post(f"{BASE_URL}/cases/{target_case}/review", json=review_data, headers=headers)
print("Review Response:", review_resp.json())

# 4. Check Audit Logs
print("\nFetching recent Audit Logs...")
audit_resp = requests.get(f"{BASE_URL}/audit-logs", headers=headers).json()
print("Found Audit Logs:", len(audit_resp))
for log in audit_resp[:5]:
    print(f"- {log['action']}: {log['metadata_json']}")
