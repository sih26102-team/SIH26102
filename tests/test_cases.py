import requests
import json

BASE_URL = "http://localhost:8001"

def get_token(username):
    resp = requests.post(f"{BASE_URL}/auth/verify-otp", json={"username": username, "otp": "123456"})
    return resp.json().get("access_token")

# 1. District Auth creates a case
district_token = get_token("district.demo")
dh_headers = {"Authorization": f"Bearer {district_token}"}

print("Creating Case...")
case_resp = requests.post(f"{BASE_URL}/cases", json={"project_id": "PRJ-2026-1042"}, headers=dh_headers)
print("Create Case:", case_resp.json())
case_id = case_resp.json()["case_id"]

# 2. District Auth approves case
print("\nApproving Case...")
approve_resp = requests.post(f"{BASE_URL}/cases/{case_id}/approve", headers=dh_headers)
print("Approve Case:", approve_resp.json())

# 3. District Auth assigns case to officer.demo
officer_id = 4 # Hardcoded ID for officer.demo

print(f"\nAssigning Case to Officer ID {officer_id}...")
assign_resp = requests.post(f"{BASE_URL}/cases/{case_id}/assign", json={"officer_id": officer_id}, headers=dh_headers)
print("Assign Case:", assign_resp.json())

# 4. Officer views their assignments
officer_token = get_token("officer.demo")
off_headers = {"Authorization": f"Bearer {officer_token}"}
print("\nOfficer fetching cases...")
my_cases = requests.get(f"{BASE_URL}/cases", headers=off_headers)
print("Officer Cases:", my_cases.json())

# 5. Officer updates status
print("\nOfficer accepts assignment (UNDER_INVESTIGATION)...")
status_resp = requests.patch(f"{BASE_URL}/cases/{case_id}/status", json={"status": "UNDER_INVESTIGATION"}, headers=off_headers)
print("Update Status:", status_resp.json())
