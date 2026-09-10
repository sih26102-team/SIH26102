import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, SessionLocal
from app.models import models
from app.routes import users, auth, cases
from app.core.security import get_hash_password, verify_password

# Initialize all database tables
models.Base.metadata.create_all(bind=engine)

def seed_demo_accounts():
    """Seed or update development/demo accounts for 5 Admins and 100 Field Investigators."""
    db = SessionLocal()
    try:
        existing_users = {u.username: u for u in db.query(models.User).all()}
        existing_emails = {u.email: u for u in existing_users.values()}

        # 1. Base legacy demo accounts for fallback compatibility
        if "admin.demo" not in existing_users:
            db.add(models.User(
                username="admin.demo",
                email="admin.demo@civicshield.gov.in",
                full_name="CivicShield System Administrator",
                role="admin",
                password=get_hash_password("CivicShieldAdmin@2026!"),
                is_active=True
            ))
        if "investigator.demo" not in existing_users:
            db.add(models.User(
                username="investigator.demo",
                email="investigator.demo@civicshield.gov.in",
                full_name="Senior Field Investigator",
                role="investigator",
                password=get_hash_password("CivicShield@Demo2026!"),
                is_active=True
            ))

        # 2. Load 5 Admins and 100 Investigators from seed_accounts.json
        json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend-dashboard", "src", "data", "seed_accounts.json"))
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                seed_data = json.load(f)

            # Seed Admins
            for adm in seed_data.get("admins", []):
                if adm["username"] not in existing_users and adm["email"] not in existing_emails:
                    db.add(models.User(
                        username=adm["username"],
                        email=adm["email"],
                        full_name=adm["full_name"],
                        role="admin",
                        password=get_hash_password(adm["password"]),
                        is_active=True
                    ))
                    existing_users[adm["username"]] = True
                    existing_emails[adm["email"]] = True

            # Seed 100 Investigators
            for inv in seed_data.get("investigators", []):
                if inv["username"] not in existing_users and inv["email"] not in existing_emails:
                    db.add(models.User(
                        username=inv["username"],
                        email=inv["email"],
                        full_name=inv["full_name"],
                        role="investigator",
                        password=get_hash_password(inv["password"]),
                        is_active=True
                    ))
                    existing_users[inv["username"]] = True
                    existing_emails[inv["email"]] = True

        db.commit()
        print(f"[INFO] Initialized and verified database accounts (5 Admins, 100 Investigators).")
    except Exception as e:
        print(f"[WARNING] Demo seeding skipped or error: {e}")
        db.rollback()
    finally:
        db.close()

# Run demo seeding on startup
seed_demo_accounts()

app = FastAPI(
    title="CivicShield AI - Case Management & Security API",
    description="Backend Case Management, RBAC & Investigation Workflow for SIH26102",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(users.router)
app.include_router(cases.router)

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "civicshield-case-management-api",
        "auth": "JWT Bearer + RBAC",
        "roles": ["admin", "investigator"]
    }