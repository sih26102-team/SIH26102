from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import configure_logging
from app.database.database import Base, engine, SessionLocal, get_db
from app.routes import health
from app.models import State, District, Constituency, MP, Agency, Project, Expenditure, RiskResult, User

from app.routers.auth_router import router as auth_router, get_current_user, require_role, get_password_hash
from app.routers.analytics_router import router as analytics_router
from app.routers.risk_router import router as risk_router

configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Unified Backend Data & Case Management API for SIH26102",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(health.router)

app.include_router(auth_router)
app.include_router(analytics_router)
app.include_router(risk_router)

# Basic user endpoint for fetching users
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/users")
def create_user(user_data: dict, db: Session = Depends(get_db)):
    if "password" in user_data:
        user_data["password"] = get_password_hash(user_data["password"])
    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    audit = AuditLog(actor_user_id=new_user.id, action="USER_CREATED", entity_type="User", entity_id=str(new_user.id), metadata_json=f"User {new_user.username} created")
    db.add(audit)
    db.commit()
    return {"id": new_user.id, "username": new_user.username}

@app.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int, 
    active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['MINISTRY', 'STATE_AUTHORITY', 'DISTRICT_AUTHORITY']))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = active
    
    audit = AuditLog(actor_user_id=current_user.id, action="USER_STATUS_UPDATED", entity_type="User", entity_id=str(user.id), metadata_json=f"User {user.username} active status set to {active}")
    db.add(audit)
    db.commit()
    return {"message": f"User {'activated' if active else 'deactivated'}"}
