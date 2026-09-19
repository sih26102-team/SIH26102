# CivicShield AI Deployment Architecture

## 1. Final Architecture
The production architecture uses Docker Compose to orchestrate microservices.
- Nginx Reverse Proxy (Port 80)
- Frontend Dashboard (React/Vite)
- Backend API (FastAPI - Unified Core Data, Cases, Risk, Auth)
- ML Engine (FastAPI - Isolation Forest)
- PostgreSQL Database

## 2. Why Docker Compose
Docker Compose guarantees environment parity across laptops, test servers, and production VMs. It encapsulates the network so internal services aren't exposed directly.

## 3. Docker Role
Docker completely removes the need to have Node.js, Python, or PostgreSQL installed on the local system or cloud VM. It is the sole dependency.

## 4. Frontend Deployment
The frontend is compiled to static files in a build stage and served efficiently via Alpine Nginx.

## 5. Backend Deployment
The backend runs FastAPI with Uvicorn. The unified API successfully routes auth, cases, analytics, and data via the root Nginx proxy.

## 6. PostgreSQL
Uses postgres:16-alpine with persisted volumes and automatic schema seeding on first launch.

## 7. Environment Variables
Sensitive settings are stored in .env (see .env.example).

## 8. HTTPS and Domain
Deploy to a Linux Cloud VM. Point your domain (e.g., app.civicshield.ai) to the IP. Terminate SSL (HTTPS) via Certbot/Nginx.

## 9. Startup Process
cp .env.example .env
docker compose up -d --build
