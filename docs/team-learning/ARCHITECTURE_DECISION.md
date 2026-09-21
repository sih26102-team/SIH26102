# Architecture Decision: Monolithic Data vs Microservices

## The Problem
During development, the team struggled with whether to strictly separate the ackend-data-api and ackend-case-management databases (pure microservices) or share a single database.

## The Decision
We chose a **Shared Database Architecture** using Neon PostgreSQL. Both FastAPI applications connect to the same database.

## Why?
1. **Speed of Development**: We only have 36 hours. Implementing distributed transactions (Sagas) or data duplication between microservices would have derailed the project.
2. **Domain Cohesion**: The Case Management API fundamentally relies on the same Project and User entities managed by the Data API.
3. **Statutory Requirements**: Features like the 15% SC / 7.5% ST area funding minimums require calculating across ALL projects instantly. A shared DB makes aggregation queries trivial.
