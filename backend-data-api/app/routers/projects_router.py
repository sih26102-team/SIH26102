from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from sqlalchemy import func
from app.database.database import get_db
from app.models.all_models import Project, Constituency, District, State

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/")
def get_projects(
    state_id: Optional[int] = None,
    district_id: Optional[int] = None,
    constituency_id: Optional[int] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    sc_st_area_only: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Project)
    
    if state_id:
        query = query.filter(Project.state_id == state_id)
    if district_id:
        query = query.filter(Project.district_id == district_id)
    if constituency_id:
        query = query.filter(Project.constituency_id == constituency_id)
    if category:
        query = query.filter(Project.category == category)
    if status:
        query = query.filter(Project.project_status == status)
    if sc_st_area_only:
        query = query.filter(Project.sc_st_area_flag == True)
        
    projects = query.offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}")
def get_project_by_id(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/summary/stats")
def get_project_stats(state_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(
        func.count(Project.project_id).label("total_projects"),
        func.sum(Project.sanctioned_amount).label("total_sanctioned"),
        func.sum(Project.expenditure).label("total_expenditure")
    )
    if state_id:
        query = query.filter(Project.state_id == state_id)
        
    result = query.first()
    return {
        "total_projects": result.total_projects or 0,
        "total_sanctioned": result.total_sanctioned or 0,
        "total_expenditure": result.total_expenditure or 0
    }
