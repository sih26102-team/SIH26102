# SIH26102 Team Ownership & Module Architecture

## Team Members & Reposibilities

### Mokshagna (Backend Data API & DevOps)
- **Role**: Data Infrastructure Lead
- **Responsibilities**: 
  - Monolithic PostgreSQL Database Architecture (Neon DB)
  - Core ackend-data-api for fast data retrieval
  - eSAKSHI state machine financial modeling
  - Docker & Render Deployment configuration

### Poornesh (Backend Case Management)
- **Role**: Workflow & Monitoring Lead
- **Responsibilities**:
  - ackend-case-management workflows (inspections, flags)
  - JWT Authentication integration
  - API communication with ML Engine
  
### Charitha (Frontend Dashboard)
- **Role**: Frontend Lead
- **Responsibilities**:
  - React/Vite interactive dashboard
  - Integration with Recharts for anomaly graphs
  - State management for user roles

### Anjali (Data Pipeline & Synthetic Gen)
- **Role**: Data Engineering Lead
- **Responsibilities**:
  - data-pipeline synthetic generation scripts
  - Implementation of CAG anomalies (75-day rule, 50-lakh rule)
  - Ensuring the ML engine has realistic training ground truth

### Eswar & Karthik (ML Engine & AI Research)
- **Role**: AI / ML Leads
- **Responsibilities**:
  - ml-engine FastAPI microservice
  - Risk scoring and anomaly detection models
  - Integration of Python ML libraries (Scikit-Learn, Pandas)

## Architecture Paradigm
We are using a **Shared Database Microservices** pattern. While we have multiple backend APIs (Data API, Case API, ML Engine), the two core transactional APIs share the single Neon PostgreSQL database as a monolithic data store. This allows rapid prototyping without complex distributed transactions, while still giving Mokshagna and Poornesh isolated codebases to develop their respective features.
