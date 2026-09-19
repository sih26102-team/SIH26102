import requests
import json
import os

BASE_URL = "http://localhost:8001"

# 1. Login as officer.demo
resp = requests.post(f"{BASE_URL}/auth/verify-otp", json={"username": "officer.demo", "otp": "123456"})
token = resp.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# 2. Get my assigned projects
print("Fetching Officer Assigned Projects...")
my_cases = requests.get(f"{BASE_URL}/inspections/my-projects", headers=headers).json()
print("My Projects:", my_cases)

if not my_cases:
    print("No cases assigned. Exiting.")
    exit()
    
target_case = my_cases[0]["case_id"]

# 3. Create dummy photo
with open("dummy_photo.jpg", "w") as f:
    f.write("fake image data")

# 4. Submit Inspection
print(f"\nSubmitting Inspection for Case {target_case}...")
data = {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "physical_progress_observed": 55.5,
    "site_condition": "Work is halted due to weather.",
    "financial_observation": "Funds seemingly diverted.",
    "general_observation": "Contractor not on site.",
    "recommendation": "Pause further funding pending audit.",
    "checklist": json.dumps({"locationVerified": True, "physicalWorkExists": True})
}
files = {
    "photo": ("dummy_photo.jpg", open("dummy_photo.jpg", "rb"), "image/jpeg")
}

submit_resp = requests.post(f"{BASE_URL}/inspections/{target_case}/submit", data=data, files=files, headers=headers)
print("Submit Response:", submit_resp.json())

# Cleanup
os.remove("dummy_photo.jpg")

# 5. Verify Case Status updated to EVIDENCE_SUBMITTED
case_resp = requests.get(f"{BASE_URL}/cases/{target_case}", headers=headers).json()
print("\nNew Case Status:", case_resp["case"]["status"])
