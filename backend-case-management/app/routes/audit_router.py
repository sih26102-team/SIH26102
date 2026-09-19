from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import Case, Project, User, AuditLog, Inspection, Evidence
from app.routes.auth_utils import get_current_user

router = APIRouter(prefix="/audit-logs", tags=["audit"])

@router.get("")
def get_audit_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Restrict to MIN, STATE, DIST. Or if Officer, only their logs.
    if current_user.role == "INSPECTION_OFFICER":
        return db.query(AuditLog).filter(AuditLog.actor_user_id == current_user.id).order_by(AuditLog.timestamp.desc()).all()
        
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
