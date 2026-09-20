# CivicShield AI - Team Ownership & Architecture

## System Architecture Overview

The CivicShield AI system is designed using a bounded-context microservice architecture. To ensure high maintainability, clear team ownership, and isolated scaling, the application is divided into distinct top-level domains.

```text
      Frontend (Chandana)
           |
       Nginx Proxy
       /         \
   /works       /cases
   /auth        /inspections
  /analytics    /audit
    |               |
Backend API      Backend Case
(Mokshagna)      Management
    |            (Poornesh)
    |               |
    \-------------/
           |
   Shared PostgreSQL Database (Phaneendra)
           |
      ML Engine (Kousic & Mohith)
```

---

## 1. Mokshagna: Backend Data API & System Architecture
**Directory:** `backend-data-api/`
- **Responsibilities:** Core FastAPI structure, general APIs, authentication (JWT), dashboard analytics, project data retrieval, and serving as the primary bridge between the frontend and the ML engine.
- **Key Understanding:** Understands the HTTP request flow, database interaction for core entities (`Project`, `User`, `Agency`), and how the backend safely isolates the heavy ML Engine via internal API calls.

## 2. Poornesh: Backend Case Management & Investigation Workflow
**Directory:** `backend-case-management/`
- **Responsibilities:** The entire lifecycle of an investigation. Case creation, officer assignment, physical inspection checklists, evidence handling, and audit logging.
- **Key Understanding:** Understands how a high-risk ML output triggers the human-in-the-loop workflow. Knows how the Case service maps read-only references to the Core Database to execute relationships without tangling Python dependencies.

## 3. Chandana: Frontend & Product UX
**Directory:** `frontend/`
- **Responsibilities:** Dashboard UI, interactive charts (Recharts), mapping (React Leaflet), project views, and unifying the HTTP calls to both backend microservices.
- **Key Understanding:** Understands React state management, how Vite builds the application, and how Axios interceptors attach JWT tokens to every request.

## 4. Kousic: Cybersecurity & ML Anomaly Detection
**Directory:** `ml-engine/` (Shared)
- **Responsibilities:** RBAC/security validation on the frontend, input sanitization, and tuning the anomaly detection models. 
- **Key Understanding:** Can explain why AI doesn't "declare fraud" automatically but instead flags risk reasons for human verification, preventing false positives.

## 5. Phaneendra: Data Architecture & Data Pipeline
**Directory:** `data-pipeline/`
- **Responsibilities:** Data cleaning scripts, PostgreSQL schema design (`01_schema.sql`), feature preparation for the ML engine, and the initial database seeding.
- **Key Understanding:** Understands how messy raw CSV data is normalized into structured SQL tables and how foreign keys protect data integrity across Mokshagna and Poornesh's domains.

## 6. Mohith: Cloud, DevOps & MLOps
**Directory:** `cloud-devops/`, `docker-compose.yml`, `nginx/`
- **Responsibilities:** Containerization of all 4 services (Frontend, Data API, Case API, ML Engine). Managing Nginx reverse proxy routing and ensuring smooth deployment.
- **Key Understanding:** Can explain how `docker-compose up` orchestrates the entire system, how containers network with each other internally, and how Nginx routes external traffic to the correct microservice securely.
