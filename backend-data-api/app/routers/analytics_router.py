from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict

from app.database.database import get_db
from app.models import Project, District, State, Expenditure
from app.routers.auth_router import get_current_user, User

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Base query for projects depending on role
    query = db.query(Project)
    
    if current_user.role == "STATE_AUTHORITY":
        query = query.filter(Project.state_id == current_user.state_id)
    elif current_user.role == "DISTRICT_AUTHORITY":
        query = query.filter(Project.district_id == current_user.district_id)
        
    total_projects = query.count()
    
    # Sum of sanctioned amount
    total_budget = db.query(func.sum(Project.sanctioned_amount)).filter(Project.project_id.in_(query.with_entities(Project.project_id))).scalar() or 0
    
    # Status breakdown
    status_counts = db.query(Project.project_status, func.count(Project.project_id))\
        .filter(Project.project_id.in_(query.with_entities(Project.project_id)))\
        .group_by(Project.project_status).all()
        
    status_dict = {status: count for status, count in status_counts}

    return {
        "total_projects": total_projects,
        "total_budget": float(total_budget),
        "status_breakdown": status_dict
    }

@router.get("/trends")
def get_trends(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Simplistic trend based on creation/sanction dates or just status
    query = db.query(Project)
    if current_user.role == "STATE_AUTHORITY":
        query = query.filter(Project.state_id == current_user.state_id)
    elif current_user.role == "DISTRICT_AUTHORITY":
        query = query.filter(Project.district_id == current_user.district_id)
        
    # Example trend: group by category
    category_counts = db.query(Project.category, func.count(Project.project_id))\
        .filter(Project.project_id.in_(query.with_entities(Project.project_id)))\
        .group_by(Project.category).all()
        
    return [{"category": cat, "count": count} for cat, count in category_counts]

@router.get("/districts")
def get_district_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Group stats by district
    query = db.query(District.district_name, func.count(Project.project_id), func.sum(Project.sanctioned_amount))\
        .join(Project, District.district_id == Project.district_id)
        
    if current_user.role == "STATE_AUTHORITY":
        query = query.filter(District.state_id == current_user.state_id)
    elif current_user.role == "DISTRICT_AUTHORITY":
        query = query.filter(District.district_id == current_user.district_id)
        
    stats = query.group_by(District.district_name).all()
    
    return [
        {
            "district_name": row[0],
            "total_projects": row[1],
            "total_budget": float(row[2] or 0)
        }
        for row in stats
    ]
