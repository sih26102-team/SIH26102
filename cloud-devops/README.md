# Cloud + DevOps + MLOps — Owner: Mohith

## Secrets & Environment Variables
- Real values live in a root `.env` — never committed (`.gitignore` already covers it).
- Copy the template to get started: `cp .env.example .env`
- Never share real values over chat — if a teammate needs one, send it privately.
- CI/CD (Module 4) and cloud deployment use GitHub Actions secrets / GCP Secret Manager instead — never hardcoded in YAML or Dockerfiles.