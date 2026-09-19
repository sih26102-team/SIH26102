from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.database.database import get_db
from app.models import Case, Project, User, AuditLog, Inspection, Evidence
from app.routes.auth_utils import get_current_user

router = APIRouter(prefix="/cases", tags=["cases"])

class CaseCreate(BaseModel):
    project_id: str

class AssignRequest(BaseModel):
    officer_id: int

class StatusUpdate(BaseModel):
    status: str
    resolution: Optional[str] = None

def create_audit(db, actor_id, action, entity_type, entity_id, metadata_json):
    audit = AuditLog(
        actor_user_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        metadata_json=metadata_json
    )
    db.add(audit)
    db.commit()

@router.post("")
def create_case(req: CaseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_case = Case(project_id=req.project_id, created_by=current_user.id, status="REQUESTED")
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    create_audit(db, current_user.id, "CASE_CREATED", "Case", new_case.case_id, "Case initially requested")
    return {"case_id": new_case.case_id, "project_id": new_case.project_id}

@router.get("")
def get_cases(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Case)
    if current_user.role == "DISTRICT_AUTHORITY":
        query = query.join(Project).filter(Project.district_id == current_user.district_id)
    elif current_user.role == "INSPECTION_OFFICER":
        query = query.filter(Case.assigned_officer == current_user.id)
    return query.all()

@router.get("/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if current_user.role == "INSPECTION_OFFICER" and case.assigned_officer != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this case")
        
    req = db.query(InspectionRequest).filter(InspectionRequest.project_id == case.project_id).first()
    inv = db.query(Investigation).filter(Investigation.case_id == case_id).first()
    proj = db.query(Project).filter(Project.project_id == case.project_id).first()
    risk = db.query(RiskResult).filter(RiskResult.project_id == case.project_id).first()
    
    # Fetch all inspections and evidence for append-only history
    inspections = db.query(Inspection).filter(Inspection.project_id == case.project_id).order_by(Inspection.inspection_date.desc()).all()
    evidence = []
    if inspections:
        insp_ids = [i.inspection_id for i in inspections]
        evidence = db.query(Evidence).filter(Evidence.inspection_id.in_(insp_ids)).all()
    
    return {
        "case": case,
        "project": proj,
        "inspection_request": req,
        "investigation": inv,
        "risk_result": risk,
        "inspections": inspections,
        "evidence": evidence
    }

@router.post("/{case_id}/request-inspection")
def request_inspection(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404)
        
    case.status = "REQUESTED"
    ir = InspectionRequest(project_id=case.project_id, requested_by=current_user.id, status="REQUESTED")
    db.add(ir)
    create_audit(db, current_user.id, "CASE_REQUESTED", "Case", case_id, "Inspection manually requested")
    db.commit()
    return {"message": "Inspection requested", "case": case}

@router.post("/{case_id}/approve")
def approve_case(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "DISTRICT_AUTHORITY":
        raise HTTPException(status_code=403, detail="Only District Authority can approve")
        
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404)
        
    case.status = "APPROVED"
    create_audit(db, current_user.id, "CASE_APPROVED", "Case", case_id, "Case approved by District Authority")
    db.commit()
    return {"message": "Case approved", "case": case}

@router.post("/{case_id}/reject")
def reject_case(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "DISTRICT_AUTHORITY":
        raise HTTPException(status_code=403, detail="Only District Authority can reject")
        
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404)
        
    case.status = "RESOLVED"
    case.resolution = "REJECTED"
    create_audit(db, current_user.id, "CASE_REJECTED", "Case", case_id, "Case rejected by District Authority")
    db.commit()
    return {"message": "Case rejected", "case": case}

@router.post("/{case_id}/assign")
def assign_case(case_id: int, req: AssignRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "DISTRICT_AUTHORITY":
        raise HTTPException(status_code=403)
        
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404)
        
    officer = db.query(User).filter(User.id == req.officer_id, User.role == "INSPECTION_OFFICER").first()
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")
        
    case.assigned_officer = officer.id
    case.status = "ASSIGNED"
    
    inv = Investigation(case_id=case.case_id, project_id=case.project_id, officer_id=officer.id)
    db.add(inv)
    create_audit(db, current_user.id, "CASE_ASSIGNED", "Case", case_id, f"Assigned to officer {officer.id}")
    db.commit()
    return {"message": "Assigned successfully", "case": case}

@router.post("/{case_id}/review")
def review_case(case_id: int, req: StatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "DISTRICT_AUTHORITY":
        raise HTTPException(status_code=403, detail="Only DA can review cases")
        
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404)
        
    if req.status not in ["VERIFIED", "RESOLVED", "ACTION_REQUIRED", "ESCALATED"]:
        raise HTTPException(status_code=400, detail="Invalid review status")
        
    case.status = req.status
    if req.resolution:
        case.resolution = req.resolution
        
    audit_action = "CASE_ESCALATED" if req.status in ["ACTION_REQUIRED", "ESCALATED"] else "CASE_RESOLVED"
    create_audit(db, current_user.id, audit_action, "Case", case_id, f"Case reviewed: {req.status}")
    db.commit()
    return {"message": "Review recorded", "case": case}

@router.patch("/{case_id}/status")
def update_status(case_id: int, req: StatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404)
        
    if current_user.role == "INSPECTION_OFFICER" and case.assigned_officer != current_user.id:
        raise HTTPException(status_code=403)
        
    if current_user.role == "INSPECTION_OFFICER" and req.status in ["RESOLVED", "APPROVED"]:
        raise HTTPException(status_code=403)
        
    if req.status == "UNDER_INVESTIGATION" and case.status != "UNDER_INVESTIGATION":
        create_audit(db, current_user.id, "INSPECTION_STARTED", "Case", case_id, "Officer started investigation")
        
    case.status = req.status
    if req.resolution:
        case.resolution = req.resolution
        
    create_audit(db, current_user.id, "CASE_STATUS_UPDATED", "Case", case_id, f"Status changed to {req.status}")
    db.commit()
    return {"message": "Status updated", "case": case}
