from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database.database import get_db
from app.models.all_models import Expenditure, Project

router = APIRouter(prefix="/financial", tags=["financial"])

class ExpenditureCreate(BaseModel):
    project_id: str
    amount: float
    maker_id: int

class ExpenditureUpdate(BaseModel):
    status: str
    checker_id: Optional[int] = None
    verifier_id: Optional[int] = None

@router.post("/expenditures")
def create_expenditure_request(req: ExpenditureCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.project_id == req.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    new_expenditure = Expenditure(
        project_id=req.project_id,
        amount=req.amount,
        maker_id=req.maker_id,
        status="payment_authorization"
    )
    db.add(new_expenditure)
    db.commit()
    db.refresh(new_expenditure)
    return new_expenditure

@router.put("/expenditures/{expenditure_id}/status")
def update_expenditure_status(expenditure_id: int, req: ExpenditureUpdate, db: Session = Depends(get_db)):
    expenditure = db.query(Expenditure).filter(Expenditure.expenditure_id == expenditure_id).first()
    if not expenditure:
        raise HTTPException(status_code=404, detail="Expenditure not found")
        
    if req.status not in ["payment_authorization", "payment_concurrence", "payment_executed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    expenditure.status = req.status
    if req.checker_id:
        expenditure.checker_id = req.checker_id
    if req.verifier_id:
        expenditure.verifier_id = req.verifier_id
        
    # If fully executed, update project expenditure total
    if req.status == "payment_executed":
        project = db.query(Project).filter(Project.project_id == expenditure.project_id).first()
        if project:
            if not project.expenditure:
                project.expenditure = 0
            project.expenditure += expenditure.amount
            
    db.commit()
    db.refresh(expenditure)
    return expenditure

@router.get("/projects/{project_id}/expenditures")
def get_project_expenditures(project_id: str, db: Session = Depends(get_db)):
    return db.query(Expenditure).filter(Expenditure.project_id == project_id).all()
