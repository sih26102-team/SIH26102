# 🛡️ CivicShield AI (SIH26102)
**AI-Powered Decision-Support Platform to Detect Anomalies, Fraud, and Inefficiencies in MPLADS Implementation**

---

## 🏛️ Target System Architecture & Team Integration

CivicShield AI integrates six specialized engineering modules into **ONE unified, secure civic auditing platform**:

```
                                    USER (Admin / Investigator)
                                                │
                                                ▼
                                    REACT FRONTEND (Port 3000 / Nginx 8080)
                                                │
                                                ▼ (REST / JWT)
                      ┌─────────────────────────┴─────────────────────────┐
                      ▼                                                   ▼
            BACKEND DATA API (Port 8001)                      BACKEND CASE MANAGEMENT (Port 8002)
          (Works, Anomalies, Analytics)                         (Auth, Cases, Users, Audits)
                      │                                                   │
                      ├──────────────────────────┬────────────────────────┤
                      ▼                          ▼                        ▼
              POSTGRESQL DATABASE         ML RISK ENGINE            EVIDENCE STORE
              (Port 5432 - sih26102_db)  (Inference API 8003)      (/uploads / static)
```

### 👥 Team Module Ownership & Integration Matrix
* **Phaneendra (Data Engineer / Data Architect)**: Ingests, standardizes, and validates MPLADS datasets across eSAKSHI central nodes and district edge records (`data-pipeline/`).
* **Mokshagna (Backend Lead - Data API)**: Provides core REST APIs for works, anomaly lists, and aggregate district/state financial analytics (`backend-data-api/`).
* **Poornesh (Backend Lead - Case Management & Security)**: Implements role-based access control (RBAC), multi-state investigation workflows, and immutable audit logs (`backend-case-management/`).
* **Kousic (Cybersecurity & ML Lead)**: Builds the 8-dimensional Hybrid Risk Engine, 18% GST burn rate adjustments, and statutory explainability layer (`ml-engine/`).
* **Mohith (Cloud DevOps & MLOps Lead)**: Manages containerization, Docker Compose orchestration, service networking, and Nginx reverse proxy gateway (`cloud-devops/` & `nginx/`).
* **Chandana (Frontend Lead)**: Develops the React 18 / Vite / TailwindCSS auditing console, SLA widgets, case investigation drawers, and geolocation capture UI (`frontend-dashboard/`).

---

## 🔐 Authentication, Roles & Demo Accounts

### 1. Mandatory Security Policy: **NO PUBLIC REGISTRATION**
* Public user self-registration is strictly **disabled**.
* Only authorized Administrators can provision new Investigator accounts via the **Investigator Management Console** (`/investigators`).

### 2. Pre-Seeded Demonstration Accounts (Local / Hackathon Testing)
> [!IMPORTANT]
> These credentials are for local development and demonstration only. They must be changed before any production deployment.

| Role | Username | Password | Official Identifier |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin.demo` | `CivicShieldAdmin@2026!` | `admin.demo@civicshield.gov.in` |
| **Field Investigator** | `investigator.demo` | `CivicShield@Demo2026!` | `investigator.demo@civicshield.gov.in` |

---

## 🗄️ Database Inspection Guide

CivicShield AI uses PostgreSQL (`sih26102_db`).

### Inspecting Users & Roles
```sql
-- View all authorized users and their active statuses
SELECT id, username, email, role, is_active, created_at FROM users;
```

### Inspecting Investigations & Field Evidence
```sql
-- View all investigation cases and status
SELECT id, title, flagged_work_id, status, risk_score, latitude, longitude FROM cases;

-- View immutable audit trail for a case
SELECT id, case_id, action, performed_by_id, timestamp, details FROM case_audit_logs ORDER BY timestamp DESC;
```

---

## 🚀 How to Run Locally

### Option 1: One-Command Startup (Recommended with Docker Compose)
```bash
# Start all 6 microservices (Postgres, ML Engine, Data API, Case Mgmt, Frontend, Nginx)
docker-compose up --build
```
* **Frontend Audit Dashboard**: [http://localhost:3000](http://localhost:3000) (or via Nginx gateway at [http://localhost:8080](http://localhost:8080))
* **Backend Case API Docs**: [http://localhost:8002/docs](http://localhost:8002/docs)
* **Backend Data API Docs**: [http://localhost:8001/docs](http://localhost:8001/docs)
* **ML Engine Docs**: [http://localhost:8003/docs](http://localhost:8003/docs)

---

### Option 2: Standalone Local Startup (Without Docker)

#### Terminal 1: Backend Case Management & Auth API
```bash
cd backend-case-management
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2: Backend Data & Works API
```bash
cd backend-data-api
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### Terminal 3: ML Risk Engine
```bash
cd ml-engine
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

#### Terminal 4: React Frontend Console
```bash
cd frontend-dashboard
npm install
npm run dev
```

---

## 🔄 The 20-Step End-to-End Investigation Demo Workflow

1. **Step 1**: Admin logs in using `admin.demo` / `CivicShieldAdmin@2026!`.
2. **Step 2**: Admin views the central dashboard with national/state MPLADS anomaly KPIs.
3. **Step 3**: Admin opens the **Flagged Works** register.
4. **Step 4**: Admin identifies **Project #1042 / PRJ-2026-003** with a **High Risk Score (87/100)**.
5. **Step 5**: Admin opens the project detail page.
6. **Step 6**: System displays the **"ANOMALY ≠ FRAUD"** notice along with algorithmic burn-rate and statutory SLA explanations.
7. **Step 7**: Investigator logs in using `investigator.demo` / `CivicShield@Demo2026!`.
8. **Step 8**: Investigator opens Project #1042.
9. **Step 9**: Investigator clicks **"Request Formal Investigation"** and provides field audit justification.
10. **Step 10**: Case state transitions to `REQUESTED`; Admin receives the request in the Case Management queue.
11. **Step 11**: Admin reviews the request and clicks **"Approve & Assign"** to the investigator.
12. **Step 12**: Case state transitions to `ASSIGNED`.
13. **Step 13**: Investigator opens the assigned case in their queue.
14. **Step 14**: Investigator visits the physical construction site.
15. **Step 15**: Investigator clicks **"Submit Field Inspection & Evidence"** and uploads a site photograph.
16. **Step 16**: System captures genuine device GPS coordinates (`latitude`, `longitude`, `timestamp`) via browser geolocation.
17. **Step 17**: Investigator enters structured findings (*Site Condition*, *Financial Observation*, *Recommendation*).
18. **Step 18**: Investigator submits report; Case transitions to `EVIDENCE_SUBMITTED`.
19. **Step 19**: Admin reviews the photographic evidence, GPS proof, and structured notes.
20. **Step 20**: Admin marks the case as **RESOLVED** (or **ESCALATED**); immutable audit log permanently records the complete history.
