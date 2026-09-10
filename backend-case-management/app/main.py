from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, SessionLocal
from app.models import models
from app.routes import users, auth, cases
from app.core.security import get_hash_password, verify_password

# Initialize all database tables
models.Base.metadata.create_all(bind=engine)

def seed_demo_accounts():
    """Seed or update development/demo accounts for Admin and Investigator testing."""
    db = SessionLocal()
    try:
        # 1. Admin Demo Account
        admin_user = db.query(models.User).filter(
            (models.User.username == "admin.demo") | (models.User.email == "admin.demo@civicshield.gov.in")
        ).first()

        admin_pwd = "CivicShieldAdmin@2026!"
        if not admin_user:
            admin_user = models.User(
                username="admin.demo",
                email="admin.demo@civicshield.gov.in",
                full_name="CivicShield System Administrator",
                role="admin",
                password=get_hash_password(admin_pwd),
                is_active=True
            )
            db.add(admin_user)
            print("[INFO] Seeded Demo Admin: admin.demo / CivicShieldAdmin@2026!")
        else:
            if not verify_password(admin_pwd, admin_user.password):
                admin_user.password = get_hash_password(admin_pwd)
                admin_user.role = "admin"
                admin_user.is_active = True
                print("[INFO] Re-hashed Demo Admin password")

        # 2. Investigator Demo Account
        inv_user = db.query(models.User).filter(
            (models.User.username == "investigator.demo") | (models.User.email == "investigator.demo@civicshield.gov.in")
        ).first()

        inv_pwd = "CivicShield@Demo2026!"
        if not inv_user:
            inv_user = models.User(
                username="investigator.demo",
                email="investigator.demo@civicshield.gov.in",
                full_name="Senior Field Investigator",
                role="investigator",
                password=get_hash_password(inv_pwd),
                is_active=True
            )
            db.add(inv_user)
            print("[INFO] Seeded Demo Investigator: investigator.demo / CivicShield@Demo2026!")
        else:
            if not verify_password(inv_pwd, inv_user.password):
                inv_user.password = get_hash_password(inv_pwd)
                inv_user.role = "investigator"
                inv_user.is_active = True
                print("[INFO] Re-hashed Demo Investigator password")

        db.commit()
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