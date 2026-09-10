from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.schemas import schemas
from app.database.database import get_db
from app.models.models import Case, User, CaseAuditLog
from app.core.Oauth2 import get_current_user, get_current_user_admin

router = APIRouter(
    prefix="/cases",
    tags=["Cases & Investigation Workflow"]
)


def log_case_audit(
    db: Session,
    case_id: int,
    action: str,
    old_value: Optional[str],
    new_value: Optional[str],
    user_id: int,
    details: Optional[str] = None
):
    entry = CaseAuditLog(
        case_id=case_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        details=details,
        performed_by_id=user_id,
        timestamp=datetime.utcnow()
    )
    db.add(entry)
    db.commit()


@router.get("/", response_model=List[schemas.CaseResponse])
def get_cases(
    status_filter: Optional[str] = Query(None, alias="status"),
    work_id: Optional[str] = Query(None, alias="flagged_work_id"),
    search: Optional[str] = "",
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List cases.
    - Admin: Views all cases across the system.
    - Investigator: Views cases assigned to them or requested by them.
    """
    query = db.query(Case)

    if search:
        query = query.filter((Case.title.ilike(f"%{search}%")) | (Case.flagged_work_id.ilike(f"%{search}%")))

    if status_filter:
        query = query.filter(Case.status == status_filter.upper())

    if work_id:
        query = query.filter(Case.flagged_work_id == work_id)

    if current_user.role != "admin":
        query = query.filter(
            (Case.assigned_to_id == current_user.id) | (Case.requested_by_id == current_user.id)
        )

    return query.order_by(Case.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{id}", response_model=schemas.CaseResponse)
def get_case(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve details for a single investigation case."""
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case #{id} not found")

    if current_user.role != "admin" and case.assigned_to_id != current_user.id and case.requested_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this investigation case")

    return case


@router.get("/{id}/audit", response_model=List[schemas.CaseAuditLogResponse])
def get_case_audit(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve immutable audit logs for a case."""
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case #{id} not found")

    if current_user.role != "admin" and case.assigned_to_id != current_user.id and case.requested_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to audit history")

    return db.query(CaseAuditLog).filter(CaseAuditLog.case_id == id).order_by(CaseAuditLog.timestamp.desc()).all()


@router.post("/request", status_code=status.HTTP_201_CREATED, response_model=schemas.CaseResponse)
def request_investigation(
    payload: schemas.RequestInvestigation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Investigator Action: Submit an investigation request for an anomalous project.
    Creates a case in 'REQUESTED' state pending Admin approval.
    """
    # Check if an active case already exists for this project
    existing = db.query(Case).filter(
        Case.flagged_work_id == payload.flagged_work_id,
        Case.status.in_(["REQUESTED", "APPROVED", "ASSIGNED", "UNDER_INVESTIGATION", "EVIDENCE_SUBMITTED", "UNDER_REVIEW"])
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An active investigation case (#{existing.id}) already exists for project {payload.flagged_work_id}"
        )

    new_case = Case(
        title=payload.title,
        description=payload.description or f"Investigation requested by {current_user.full_name or current_user.username}",
        status="REQUESTED",
        flagged_work_id=payload.flagged_work_id,
        risk_score=payload.risk_score,
        risk_level=payload.risk_level,
        flagged_reasons=payload.flagged_reasons,
        requested_by_id=current_user.id,
        request_reason=payload.request_reason
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    log_case_audit(
        db=db,
        case_id=new_case.id,
        action="INVESTIGATION_REQUESTED",
        old_value=None,
        new_value="REQUESTED",
        user_id=current_user.id,
        details=f"Reason: {payload.request_reason}"
    )

    return new_case


@router.post("/assign", status_code=status.HTTP_201_CREATED, response_model=schemas.CaseResponse)
def admin_direct_assign(
    payload: schemas.AdminAssignCase,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user_admin)
):
    """
    Admin Action: Direct assignment of an anomalous project to an investigator.
    Creates or updates a case directly to 'ASSIGNED' state.
    """
    investigator = db.query(User).filter(User.id == payload.investigator_id, User.is_active == True).first()
    if not investigator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned investigator not found or inactive")

    new_case = Case(
        title=payload.title,
        description=payload.description or f"Directly assigned by Admin {admin.username}",
        status="ASSIGNED",
        flagged_work_id=payload.flagged_work_id,
        risk_score=payload.risk_score,
        risk_level=payload.risk_level,
        flagged_reasons=payload.flagged_reasons,
        assigned_to_id=investigator.id
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    log_case_audit(
        db=db,
        case_id=new_case.id,
        action="ADMIN_DIRECT_ASSIGNMENT",
        old_value=None,
        new_value=f"ASSIGNED to {investigator.username}",
        user_id=admin.id,
        details=f"Admin directly assigned investigation to investigator ID {investigator.id}"
    )

    return new_case


@router.post("/{id}/approve", response_model=schemas.CaseResponse)
def approve_investigation_request(
    id: int,
    payload: schemas.ApproveInvestigation,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user_admin)
):
    """
    Admin Action: Approve a pending investigation request and assign an investigator.
    """
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if case.status != "REQUESTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve case in status '{case.status}'. Only 'REQUESTED' cases can be approved."
        )

    # Assign to specified investigator or fallback to requester
    assignee_id = payload.investigator_id or case.requested_by_id
    if assignee_id:
        assignee = db.query(User).filter(User.id == assignee_id, User.is_active == True).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned investigator not found")
        case.assigned_to_id = assignee.id

    old_status = case.status
    case.status = "ASSIGNED"
    db.commit()
    db.refresh(case)

    log_case_audit(
        db=db,
        case_id=case.id,
        action="REQUEST_APPROVED",
        old_value=old_status,
        new_value="ASSIGNED",
        user_id=admin.id,
        details=payload.admin_notes or "Investigation request approved by Administrator"
    )

    return case


@router.post("/{id}/reject", response_model=schemas.CaseResponse)
def reject_investigation_request(
    id: int,
    payload: schemas.RejectInvestigation,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user_admin)
):
    """
    Admin Action: Reject an investigation request.
    """
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if case.status != "REQUESTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject case in status '{case.status}'"
        )

    old_status = case.status
    case.status = "REJECTED"
    case.resolution_notes = f"Rejected by Admin: {payload.rejection_reason}"
    db.commit()
    db.refresh(case)

    log_case_audit(
        db=db,
        case_id=case.id,
        action="REQUEST_REJECTED",
        old_value=old_status,
        new_value="REJECTED",
        user_id=admin.id,
        details=payload.rejection_reason
    )

    return case


@router.post("/{id}/evidence", response_model=schemas.CaseResponse)
def submit_field_evidence(
    id: int,
    payload: schemas.SubmitFieldEvidence,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Investigator Action: Upload on-site photograph, record genuine GPS coordinates, and submit findings.
    """
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if current_user.role != "admin" and case.assigned_to_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the assigned investigator can upload field evidence")

    old_status = case.status
    case.status = "EVIDENCE_SUBMITTED"

    if payload.evidence_photo_url:
        case.evidence_photo_url = payload.evidence_photo_url
    if payload.latitude is not None and payload.longitude is not None:
        case.latitude = payload.latitude
        case.longitude = payload.longitude
        case.location_timestamp = payload.location_timestamp or datetime.utcnow()

    if payload.site_condition:
        case.site_condition = payload.site_condition
    if payload.financial_observation:
        case.financial_observation = payload.financial_observation
    if payload.investigator_recommendation:
        case.investigator_recommendation = payload.investigator_recommendation
    if payload.investigator_notes:
        case.investigator_notes = payload.investigator_notes

    db.commit()
    db.refresh(case)

    coords_str = f"({case.latitude}, {case.longitude})" if case.latitude else "Location not captured"
    log_case_audit(
        db=db,
        case_id=case.id,
        action="EVIDENCE_SUBMITTED",
        old_value=old_status,
        new_value="EVIDENCE_SUBMITTED",
        user_id=current_user.id,
        details=f"GPS: {coords_str}. Notes: {payload.investigator_notes or 'Inspection findings uploaded'}"
    )

    return case


@router.post("/{id}/resolve", response_model=schemas.CaseResponse)
def resolve_or_escalate_case(
    id: int,
    payload: schemas.ResolveCase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin or Assigned Investigator Action: Close, resolve, or escalate the investigation.
    """
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if current_user.role != "admin" and case.assigned_to_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to resolve this investigation")

    old_status = case.status
    case.status = payload.resolution
    case.resolution = payload.resolution
    case.resolution_notes = payload.resolution_notes

    db.commit()
    db.refresh(case)

    log_case_audit(
        db=db,
        case_id=case.id,
        action=f"CASE_{payload.resolution}",
        old_value=old_status,
        new_value=payload.resolution,
        user_id=current_user.id,
        details=payload.resolution_notes
    )

    return case
