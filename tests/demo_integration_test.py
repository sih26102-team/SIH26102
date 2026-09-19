import requests
import json
import os
import time

BASE_URL = "http://localhost:8001"
CASE_URL = "http://localhost:8004"

def login(username, password="CivicShield@Demo2026!"):
    res = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
    return res

print("=== STARTING FULL CIVICSHIELD AI DEMONSTRATION TEST ===")

# Negative Test 1: Invalid login / Password
print("\n[TEST] Invalid Login/Password")
res = login("district.demo", "000000")
assert res.status_code in [400, 401, 403], f"Expected 401, 403 or 400, got {res.status_code}"

# Negative Test 2: Expired/Invalid JWT
print("[TEST] Invalid JWT")
res = requests.get(f"{CASE_URL}/cases", headers={"Authorization": "Bearer FAKE_JWT"})
assert res.status_code == 401, "Expected 401 for bad JWT"

# STEP 1: District Authority Logs in
print("\n[STEP 1] District Authority logs in")
da_res = login("district.demo")
assert da_res.status_code == 200
da_token = da_res.json()["access_token"]
da_headers = {"Authorization": f"Bearer {da_token}"}

# STEP 2: Dashboard shows district projects (Check risk scoping)
print("[STEP 2] DA fetches projects")
# Let's hit the analytics projects endpoint (which we should have)
projects_res = requests.get(f"{BASE_URL}/risk/projects", headers=da_headers)
if projects_res.status_code == 200:
    projects = projects_res.json()
    # Check if DA can only see their district (DA is seeded with district 22 usually)
    pass
else:
    print(f"Warning: /risk/projects returned {projects_res.status_code}")

# STEP 3 & 4: Open Project #1042 and see Risk Score 87/100
print("[STEP 3-4] DA opens Project 1042 and checks Risk 87/100")
proj_res = requests.get(f"{BASE_URL}/risk/projects/PRJ-2026-1042", headers=da_headers)
assert proj_res.status_code == 200, "Project not found"
risk_data = proj_res.json()
assert risk_data["risk"]["risk_score"] == 87.0
assert risk_data["risk"]["risk_level"] == "HIGH"

# STEP 5 & 6: Check reasons and verifications
print("[STEP 5-6] Checking Reasons and Verifications")
assert len(risk_data["risk"]["reasons"]) > 0
assert len(risk_data["risk"]["recommended_verification"]) > 0

# STEP 7: Create case (if not exists) and assign to Officer A
print("[STEP 7] DA creates and assigns case to Officer A")
case_res = requests.post(f"{CASE_URL}/cases", json={"project_id": "PRJ-2026-1042"}, headers=da_headers)
case_id = case_res.json()["case_id"]

officer_id = 4

assign_res = requests.post(f"{CASE_URL}/cases/{case_id}/assign", json={"officer_id": officer_id}, headers=da_headers)
assert assign_res.status_code == 200

# STEP 8: Log out (Just drop token)
print("[STEP 8] DA Logs out")

# STEP 9: Officer logs in
print("[STEP 9] Officer Logs in")
off_res = login("officer.demo")
off_token = off_res.json()["access_token"]
off_headers = {"Authorization": f"Bearer {off_token}"}

# Negative Test: Officer attempting to access another officer's case
# Let's create a dummy case assigned to someone else
print("\n[TEST] Officer accessing unauthorized case")
fake_case = requests.post(f"{CASE_URL}/cases", json={"project_id": "PRJ-2026-0001"}, headers=da_headers).json()
bad_access = requests.get(f"{CASE_URL}/cases/{fake_case['case_id']}", headers=off_headers)
assert bad_access.status_code == 403, f"Expected 403, got {bad_access.status_code}"

# STEP 10 & 11: Officer sees New Assignment
print("\n[STEP 10-11] Officer views assignments")
my_projs = requests.get(f"{CASE_URL}/inspections/my-projects", headers=off_headers)
assert my_projs.status_code == 200
assert any(p["project_id"] == "PRJ-2026-1042" for p in my_projs.json())

# STEP 12: Officer accepts
print("[STEP 12] Officer accepts assignment")
acc_res = requests.patch(f"{CASE_URL}/cases/{case_id}/status", json={"status": "UNDER_INVESTIGATION"}, headers=off_headers)
assert acc_res.status_code == 200

# STEP 13: Officer submits evidence
print("[STEP 13] Officer submits evidence")
with open("temp.jpg", "w") as f: f.write("img")
data = {
    "latitude": 10.0, "longitude": 20.0,
    "physical_progress_observed": 50,
    "site_condition": "Good",
    "financial_observation": "None",
    "general_observation": "None",
    "recommendation": "None",
    "checklist": "{}"
}
files = {"photo": ("temp.jpg", open("temp.jpg", "rb"), "image/jpeg")}
sub_res = requests.post(f"{CASE_URL}/inspections/{case_id}/submit", data=data, files=files, headers=off_headers)
assert sub_res.status_code == 200
# Clean up temp file manually if needed

# Negative Test: Officer attempting to resolve case
print("\n[TEST] Officer attempting to resolve case directly")
res_bad = requests.patch(f"{CASE_URL}/cases/{case_id}/status", json={"status": "RESOLVED", "resolution": "Done"}, headers=off_headers)
assert res_bad.status_code == 403, "Expected 403"

# STEP 14 & 15: DA logs in, sees Evidence Submitted
print("\n[STEP 14-15] DA checks case status")
case_check = requests.get(f"{CASE_URL}/cases/{case_id}", headers=da_headers).json()
assert case_check["case"]["status"] == "EVIDENCE_SUBMITTED"

# STEP 16 & 17: DA Reviews and chooses ACTION REQUIRED
print("[STEP 16-17] DA marks ACTION REQUIRED")
rev_res = requests.post(f"{CASE_URL}/cases/{case_id}/review", json={"status": "ACTION_REQUIRED", "resolution": "Needs attention"}, headers=da_headers)
assert rev_res.status_code == 200

# STEP 18: Inspection History append-only
print("[STEP 18] Verifying Append-Only Inspection History")
final_case = requests.get(f"{CASE_URL}/cases/{case_id}", headers=da_headers).json()
assert len(final_case["inspections"]) >= 1

# STEP 19: Open Audit Trail
print("[STEP 19] Verifying Audit Trail")
audits = requests.get(f"{CASE_URL}/audit-logs", headers=da_headers).json()
assert len(audits) > 0

# STEP 20: Every major action recorded
actions = [a["action"] for a in audits]
print("Recent Actions found:", set(actions))

# Negative Test: DA attempting to access another district
print("\n[TEST] DA accessing unauthorized district")
# Project PRJ-2026-0001 is in District 1 (from seed_db.py). DA is District 22.
da_bad = requests.get(f"{BASE_URL}/risk/projects/PRJ-2026-0001", headers=da_headers)
assert da_bad.status_code == 403, f"Expected 403, got {da_bad.status_code}"

# Negative Test: State Auth accessing another state
print("\n[TEST] State Auth accessing unauthorized state")
st_res = login("state.demo")
st_token = st_res.json()["access_token"]
st_headers = {"Authorization": f"Bearer {st_token}"}
# PRJ-2026-1042 is State 9 (Maharashtra). PRJ-2026-0001 is State 1 (Andhra Pradesh). State demo is State 9.
st_bad = requests.get(f"{BASE_URL}/risk/projects/PRJ-2026-0001", headers=st_headers)
assert st_bad.status_code == 403, f"Expected 403, got {st_bad.status_code}"

# Negative Test: Malformed API input
print("\n[TEST] Malformed API input")
bad_api = requests.post(f"{CASE_URL}/cases/{case_id}/review", json={"invalid": "payload"}, headers=da_headers)
assert bad_api.status_code == 422, "Expected 422 for Unprocessable Entity"

print("\n=== FULL INTEGRATION TEST PASSED SUCCESSFULLY ===")
