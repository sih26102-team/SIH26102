#!/bin/bash
set -e

# ---- backend-data-api (Mokshagna) ----
mkdir -p backend-data-api/app/routes backend-data-api/app/services backend-data-api/app/models \
         backend-data-api/app/schemas backend-data-api/app/database backend-data-api/app/core \
         backend-data-api/tests
echo "# Backend Data API — Owner: Mokshagna" > backend-data-api/README.md
echo "# main.py — owner: Mokshagna" > backend-data-api/app/main.py
for f in works analytics health; do echo "# $f.py — owner: Mokshagna" > backend-data-api/app/routes/$f.py; done
touch backend-data-api/app/services/.gitkeep backend-data-api/app/models/.gitkeep \
      backend-data-api/app/schemas/.gitkeep backend-data-api/app/database/.gitkeep \
      backend-data-api/app/core/.gitkeep backend-data-api/tests/.gitkeep
touch backend-data-api/requirements.txt

# ---- backend-case-management (Poornesh) ----
mkdir -p backend-case-management/app/routes backend-case-management/app/services backend-case-management/app/models \
         backend-case-management/app/schemas backend-case-management/app/database backend-case-management/app/core \
         backend-case-management/tests
echo "# Backend Case Management — Owner: Poornesh" > backend-case-management/README.md
echo "# main.py — owner: Poornesh" > backend-case-management/app/main.py
for f in auth cases users; do echo "# $f.py — owner: Poornesh" > backend-case-management/app/routes/$f.py; done
touch backend-case-management/app/services/.gitkeep backend-case-management/app/models/.gitkeep \
      backend-case-management/app/schemas/.gitkeep backend-case-management/app/database/.gitkeep \
      backend-case-management/app/core/.gitkeep backend-case-management/tests/.gitkeep
touch backend-case-management/requirements.txt

# ---- frontend-dashboard (Chandana) ----
mkdir -p frontend-dashboard/src/components frontend-dashboard/src/pages frontend-dashboard/src/services \
         frontend-dashboard/src/hooks frontend-dashboard/src/utils frontend-dashboard/public frontend-dashboard/tests
echo "# Frontend Dashboard — Owner: Chandana" > frontend-dashboard/README.md
for f in LoginForm FlaggedWorksTable RiskExplanationPanel TrendChart FlaggedMap; do
  echo "// $f.jsx — owner: Chandana" > frontend-dashboard/src/components/$f.jsx
done
echo "// App.jsx — owner: Chandana" > frontend-dashboard/src/App.jsx
touch frontend-dashboard/src/pages/.gitkeep frontend-dashboard/src/services/.gitkeep \
      frontend-dashboard/src/hooks/.gitkeep frontend-dashboard/src/utils/.gitkeep \
      frontend-dashboard/public/.gitkeep frontend-dashboard/tests/.gitkeep
touch frontend-dashboard/package.json

# ---- ml-engine (Kousic) ----
mkdir -p ml-engine/app ml-engine/training ml-engine/features ml-engine/models ml-engine/tests
echo "# ML Engine — Owner: Kousic" > ml-engine/README.md
for f in main predict explain; do echo "# $f.py — owner: Kousic" > ml-engine/app/$f.py; done
for f in train_model evaluate_model; do echo "# $f.py — owner: Kousic" > ml-engine/training/$f.py; done
echo "# feature_definitions.py — owner: Kousic" > ml-engine/features/feature_definitions.py
for f in test_model test_features; do echo "# $f.py — owner: Kousic" > ml-engine/tests/$f.py; done
touch ml-engine/models/.gitkeep   # model.pkl itself is NOT created empty — Kousic commits the real trained file here
touch ml-engine/requirements.txt

# ---- data-pipeline (Phaneendra) ----
mkdir -p data-pipeline/raw_data data-pipeline/processed_data data-pipeline/scripts \
         data-pipeline/db data-pipeline/notebooks data-pipeline/tests
echo "# Data Pipeline — Owner: Phaneendra" > data-pipeline/README.md
for f in ingest clean transform; do echo "# $f.py — owner: Phaneendra" > data-pipeline/scripts/$f.py; done
touch data-pipeline/raw_data/.gitkeep data-pipeline/processed_data/.gitkeep \
      data-pipeline/db/.gitkeep data-pipeline/notebooks/.gitkeep data-pipeline/tests/.gitkeep

# ---- cloud-devops (Mohith — full depth, this is yours) ----
mkdir -p cloud-devops/docker cloud-devops/deployment/cloud cloud-devops/deployment/environment \
         cloud-devops/monitoring cloud-devops/scripts
echo "# Cloud + DevOps + MLOps — Owner: Mohith" > cloud-devops/README.md
for f in backend-data backend-case ml frontend; do
  echo "# $f.Dockerfile — written in Module 2 (Docker Fundamentals)" > cloud-devops/docker/$f.Dockerfile
done
touch cloud-devops/deployment/cloud/.gitkeep cloud-devops/deployment/environment/.gitkeep \
      cloud-devops/monitoring/.gitkeep cloud-devops/scripts/.gitkeep
echo "# Filled in during Module 3 (Env Vars & Secrets)" > cloud-devops/.env.example

# ---- shared docs ----
mkdir -p docs
for f in architecture api-contracts data_dictionary feature_catalog risk_scoring ml_evaluation security demo_flow; do
  echo "# ${f//_/ }" > docs/$f.md
done

# ---- shared tests ----
mkdir -p tests/integration tests/api tests/ml tests/end_to_end
touch tests/integration/.gitkeep tests/api/.gitkeep tests/ml/.gitkeep tests/end_to_end/.gitkeep

# ---- root files ----
# NOTE: .github/workflows lives at repo ROOT (not under cloud-devops/) —
# GitHub Actions only detects workflows here. Still yours to own and edit.
mkdir -p .github/workflows
echo "# ci-cd.yml — written in Module 4 (CI/CD & GitHub Actions)." > .github/workflows/ci-cd.yml

cat > .gitignore << 'GITIGNORE_EOF'
# Python
__pycache__/
*.py[cod]
*.egg-info/
venv/
env/
.venv/

# Environment variables
.env
*.env.local

# Node / React
node_modules/
build/
dist/

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/

# Logs
*.log
GITIGNORE_EOF

cat > README.md << 'README_EOF'
# SIH26102 — AI-Powered System to Detect Anomalies, Fraud, and Inefficiencies in MPLADS Scheme Implementation

Smart India Hackathon 2026 — Internal Selection Round

## Team & folders
| Folder | Owner | Role |
|---|---|---|
| backend-data-api/ | Mokshagna | Backend lead |
| backend-case-management/ | Poornesh | Backend lead |
| frontend-dashboard/ | Chandana | Frontend lead |
| ml-engine/ | Kousic | Security & QA / ML |
| data-pipeline/ | Phaneendra | Data engineering |
| cloud-devops/ | Mohith | Cloud + DevOps + MLOps |

## Running locally
docker-compose.yml will bring up all services together — added in Module 2.
README_EOF

echo "version: \"3.9\"

# Services added in Module 2 (Docker Fundamentals build step)
services:
" > docker-compose.yml

echo "Scaffold complete: $(find . -type f | wc -l) files created."
