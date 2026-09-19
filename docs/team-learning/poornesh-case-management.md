# Poornesh - Backend Case Management & Investigation Workflow

## Your Responsibility Area
You own the `backend-case-management/` directory. Your responsibility begins the moment a high-risk project is flagged and a District Authority clicks "Initiate Investigation". You own the entire lifecycle of a case, its inspections, evidence, and audit logs.

## Core Files You Own
- `app/routes/cases_router.py`: Handles `/api/cases` endpoints (creation, fetching assigned cases, updating status).
- `app/routes/inspections_router.py`: Handles `/api/inspections` (approving inspection requests, submitting checklist data, and evidence).
- `app/routes/audit_router.py`: Handles `/api/audit` (retrieving chronological actions for a case).
- `app/models/models.py`: Your database domain mapping (`Case`, `Inspection`, `Evidence`, `AuditLog`).

## How the Application Runs (Your Part)
When Docker starts, your code runs as a completely independent FastAPI microservice on port 8000 inside the `backend-case-management` container. Nginx automatically routes any frontend request starting with `/api/cases`, `/api/inspections`, or `/api/audit` directly to your service. 

## The Data Flow You Need to Explain
1. **Risk to Case**: A high risk result arrives from Mokshagna's API. The frontend calls `POST /api/cases` with `project_id`.
2. **Case Creation**: Your code in `cases_router.py` creates a `Case` in the database with status `REQUESTED`.
3. **Assignment**: A District Authority assigns an officer. `POST /api/cases/{id}/assign` updates the `Case.assigned_officer`.
4. **Inspection**: The officer visits the site and submits evidence. `POST /api/inspections/{id}/submit` saves the checklist and evidence metadata.
5. **Review**: The Authority reviews and marks the case `RESOLVED`.
6. **Audit Trail**: Every action above triggered `create_audit()`, allowing the frontend to call `GET /api/audit/{case_id}` to show the history.

## Likely Judge Questions
**Q: How does your case module communicate with Mokshagna's core API?**
*A: We use a modular microservice architecture. My service and his service share the same underlying PostgreSQL database but run independently. I map read-only references to his `Project` and `User` tables in my `models.py` so I can query relationships natively without tightly coupling our Python code.*

**Q: How do you verify who is assigning cases?**
*A: I share the `JWT_SECRET` with the Data API. My `auth_utils.py` intercepts the incoming token from the frontend, decodes it, and reads the user's role directly, rejecting the request if an Inspection Officer tries to assign a case.*
