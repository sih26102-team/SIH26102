# Mokshagna - Backend Data API & System Architecture

## Your Responsibility Area
You own the `backend-data-api/` directory. You are the architect of the core FastAPI runtime. Your responsibility covers the general system architecture, authentication, core data delivery (Projects, Works), and integration with the ML engine.

## Core Files You Own
- `app/routers/auth_router.py`: JWT token generation, role extraction, and password verification.
- `app/routers/works_router.py`: Handles `/api/works` endpoints (retrieving projects based on district).
- `app/routers/analytics_router.py`: Handles `/api/analytics` endpoints (aggregations for the dashboard).
- `app/routers/risk_router.py`: Acts as the bridge between the frontend and the ML Engine.
- `app/models/all_models.py`: The single source of truth for the core application domains (`User`, `Project`, `State`, `District`, `Agency`).

## How the Application Runs (Your Part)
Your FastAPI server runs as the primary `backend-data-api` microservice. When Nginx receives requests for `/api/works`, `/api/auth`, or `/api/analytics`, they are routed to your container. You provide the foundational data that the rest of the application builds upon.

## The Data Flow You Need to Explain
1. **Login**: Frontend calls `POST /api/auth/login`. You verify against the DB and issue a JWT containing the user's role and district.
2. **Dashboard Load**: Frontend calls `GET /api/works`. Your code reads the JWT, queries the `projects` table for that specific district, and returns the list.
3. **ML Integration**: The frontend requests an anomaly check. Your `risk_router.py` forwards the project data to the `ml-engine` on port 8003, retrieves the risk score, and stores the result in the `RiskResult` table before sending it back to the frontend.

## Likely Judge Questions
**Q: How is the backend separated among the team?**
*A: I designed a bounded-context microservice architecture. I own the Core Data and API layer, while Poornesh owns the Case Management layer. We run as two separate FastAPI containers behind an Nginx reverse proxy. We share the PostgreSQL database, but maintain strict domain boundaries in our SQLAlchemy models.*

**Q: How does the ML integration work?**
*A: My backend does not run ML code. Instead, my `risk_router.py` acts as an API gateway. It sends a secure internal HTTP request to the ML Engine microservice, allowing the heavy Python data science libraries to remain completely isolated from my fast API web server.*
