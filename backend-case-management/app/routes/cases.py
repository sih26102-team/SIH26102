from fastapi import APIRouter, Depends,HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional,List

from app.schemas import schemas
from app.database.database import get_db
from app.models.models import Case, User,CaseAuditLog
from app.core.Oauth2 import get_current_user 

router =  APIRouter(
    prefix = "/cases",
    tags = ["Cases"]
)


def log_audit(db: Session, case_id: int, action: str, old_value: Optional[str], new_value: Optional[str], user_id: int):
    entry = CaseAuditLog(
        case_id=case_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        performed_by_id=user_id
    )
    db.add(entry)
    db.commit()

@router.get("/{id}/audit", response_model=List[schemas.CaseAuditLogResponse])
def get_case_audit(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case with id {id} not found")

    if current_user.role != "admin" and case.assigned_to_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view audit logs for this case")

    return db.query(CaseAuditLog).filter(CaseAuditLog.case_id == id).order_by(CaseAuditLog.timestamp.desc()).all()


@router.get("/",response_model = List[schemas.CaseResponse])
def get_cases(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), limit:int = Query(10, ge = 1, le = 200), skip:int = Query(0,ge = 0), search: Optional[str] ="",include_archived: Optional[bool] = False):
    query = db.query(Case).filter(Case.title.ilike(f"%{search}%"))

    if not include_archived:
        query = query.filter(Case.status != "ARCHIVED")

    if current_user.role != "admin":
        query = query.filter(Case.assigned_to_id == current_user.id)
    return query.offset(skip).limit(limit).all()


@router.post("/",status_code = status.HTTP_201_CREATED,response_model = schemas.CaseResponse)
def create_case(case: schemas.CreateCase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_case = Case(**case.model_dump(),assigned_to_id = current_user.id)
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    log_audit(
        db=db,
        case_id=new_case.id,
        action="CREATE",
        old_value=None,
        new_value=str(case.model_dump()),
        user_id=current_user.id
    )

    return new_case


@router.get("/{id}",response_model = schemas.CaseResponse)
def get_case(id:int,db:Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Case with id {id} not found")
    if current_user.role != "admin" and case.assigned_to_id != current_user.id :
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You do not have permission to access this case")
    return case


@router.put("/{id}",response_model = schemas.CaseResponse)
def update_case(id:int, case_update: schemas.UpdateCase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case_query = db.query(Case).filter(Case.id == id)
    target_case = case_query.first()
    if not target_case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case with id {id} not found")
    if current_user.role != "admin" and target_case.assigned_to_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this case")

    if target_case.status == "ARCHIVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Archived cases are read-only and cannot be modified."
        )

    update_dict = case_update.model_dump(exclude_unset=True)
    for key, new_val in update_dict.items():
        old_val = getattr(target_case, key, None)
        if old_val != new_val:
            setattr(target_case, key, new_val)
            log_audit(
                db=db,
                case_id=id,
                action=f"UPDATE_{key.upper()}",
                old_value=str(old_val) if old_val is not None else None,
                new_value=str(new_val) if new_val is not None else None,
                user_id=current_user.id
            )

    case_query.update(update_dict,synchronize_session = False)
    db.commit()
    return case_query.first()


@router.delete("/{id}", response_model=schemas.MessageResponse)
def archive_case(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case_query = db.query(Case).filter(Case.id == id)
    case = case_query.first()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with id {id} not found"
        )

    if current_user.role != "admin" and case.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive this case"
        )

    case.status = "ARCHIVED"
    db.commit()
    
    return {"message": f"Case {id} archived successfully"}
