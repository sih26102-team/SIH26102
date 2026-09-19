from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import json
import os
import shutil

from app.database.database import get_db
from app.models import Case, Project, User, AuditLog, Inspection, Evidence
from app.routes.auth_utils import get_current_user

router = APIRouter(prefix="/inspections", tags=["inspections"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{case_id}/submit")
async def submit_inspection(
    case_id: int,
    latitude: float = Form(...),
    longitude: float = Form(...),
    physical_progress_observed: float = Form(...),
    site_condition: str = Form(...),
    financial_observation: str = Form(...),
    general_observation: str = Form(...),
    recommendation: str = Form(...),
    checklist: str = Form(...),  # JSON string
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "INSPECTION_OFFICER":
        raise HTTPException(status_code=403, detail="Only officers can submit inspections")
        
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if case.assigned_officer != current_user.id:
        raise HTTPException(status_code=403, detail="Not assigned to this case")
        
    if case.status not in ["UNDER_INVESTIGATION", "ASSIGNED"]:
        raise HTTPException(status_code=400, detail=f"Cannot submit inspection for case in status: {case.status}")

    # 1. Store Photo
    file_path = os.path.join(UPLOAD_DIR, f"case_{case_id}_{photo.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)
        
    # 2. Create Inspection Record
    inspection = Inspection(
        project_id=case.project_id,
        officer_id=current_user.id,
        latitude=latitude,
        longitude=longitude,
        physical_progress_observed=physical_progress_observed,
        site_condition=site_condition,
        financial_observation=financial_observation,
        general_observation=general_observation,
        recommendation=recommendation,
        checklist_responses=checklist,
        status="SUBMITTED"
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    
    # 3. Store Evidence Reference
    evidence = Evidence(
        inspection_id=inspection.inspection_id,
        file_reference=file_path,
        evidence_type="PHOTO"
    )
    db.add(evidence)
    
    # 4. Update Case Status
    case.status = "EVIDENCE_SUBMITTED"
    # 5. Create Audit Event
    audit = AuditLog(
        actor_user_id=current_user.id,
        action="INSPECTION_SUBMITTED",
        entity_type="Case",
        entity_id=str(case_id),
        metadata_json=f"Inspection {inspection.inspection_id} submitted for Project {case.project_id}"
    )
    db.add(audit)
    db.add(audit)
    
    db.commit()
    return {"message": "Inspection successfully submitted", "inspection_id": inspection.inspection_id}

@router.get("/my-projects")
def get_my_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch assigned projects enriched with risk data for the officer dashboard."""
    if current_user.role != "INSPECTION_OFFICER":
        raise HTTPException(status_code=403)
        
    cases = db.query(Case, Project, RiskResult)\
        .join(Project, Case.project_id == Project.project_id)\
        .outerjoin(RiskResult, Project.project_id == RiskResult.project_id)\
        .filter(Case.assigned_officer == current_user.id)\
        .all()
        
    out = []
    for c, p, r in cases:
        out.append({
            "case_id": c.case_id,
            "project_id": p.project_id,
            "project_title": p.project_title,
            "category": p.category,
            "district_id": p.district_id,
            "risk_score": r.risk_score if r else None,
            "risk_level": r.risk_level if r else "UNSCORED",
            "assignment_date": c.updated_at,
            "inspection_status": c.status
        })
    return out
