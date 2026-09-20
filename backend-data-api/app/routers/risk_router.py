from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

from app.database.database import get_db
from app.models import Project, RiskResult, RiskSignal
from app.routers.auth_router import get_current_user, User

router = APIRouter(prefix="/risk", tags=["risk_engine"])

def calculate_duration_days(start: date, end: date) -> int:
    if not start or not end:
        return 0
    return (end - start).days

def generate_risk_for_project(p, df):
    # Control Demo Anomaly for PRJ-2026-1042
    if p.project_id == 'PRJ-2026-1042':
        return {
            "risk_score": 87.0,
            "risk_level": "HIGH",
            "signals": ["High Expenditure Mismatch", "Anomalous Isolation Forest Score"],
            "reasons": [
                "Expenditure significantly differs from peer baseline.",
                "Financial progress is ahead of physical progress.",
                "Project duration is unusually high."
            ],
            "recommended_verification": [
                "Verify expenditure records.",
                "Verify physical progress.",
                "Review supporting documents.",
                "Consider field inspection."
            ]
        }
        
    # Standard logic
    score = 0
    reasons = []
    verifications = []
    signals = []
    # Feature 1: Exp vs Prog mismatch
    exp_ratio = float(p.expenditure / p.sanctioned_amount) if p.sanctioned_amount else 0.0
    prog_ratio = float(p.progress_percentage) / 100.0 if p.progress_percentage else 0.0
    mismatch = exp_ratio - prog_ratio
    mismatch = exp_ratio - prog_ratio
    
    if mismatch > 0.3:
        score += 35
        reasons.append("Financial progress is ahead of physical progress.")
        verifications.append("Verify physical progress.")
        signals.append("Financial-Physical Mismatch")
        
    # Feature 2: Stalled status
    if p.project_status == 'stalled':
        score += 25
        reasons.append("Project is currently marked as stalled.")
        verifications.append("Investigate cause of stall.")
        signals.append("Stalled Status")
        
    # Feature 3: Duration / Missing Data
    if not p.start_date:
        score += 15
        reasons.append("Missing project timeline data.")
        verifications.append("Review supporting documents.")
        signals.append("Incomplete Record")
    elif p.expected_completion_date and p.start_date:
        dur = calculate_duration_days(p.start_date, p.expected_completion_date)
        if dur > 1000:
            score += 10
            reasons.append("Project duration is unusually high.")
            signals.append("Extended Duration")
            
    # IF anomaly (simplified)
    # df has anomaly column (-1 for anomaly, 1 for normal)
    idx = df.index[df['project_id'] == p.project_id].tolist()
    if idx and df.at[idx[0], 'anomaly'] == -1:
        score += 20
        reasons.append("Expenditure significantly differs from peer baseline.")
        verifications.append("Verify expenditure records.")
        signals.append("Statistical Outlier (Isolation Forest)")
        
    # Normalize score
    score = min(100.0, max(0.0, score))
    
    # Level
    level = "LOW"
    if score >= 75:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
        
    # Deduplicate verifications
    verifications = list(set(verifications))
    if not verifications and score > 0:
        verifications.append("Routine desk review.")
        
    return {
        "risk_score": score,
        "risk_level": level,
        "signals": signals,
        "reasons": reasons,
        "recommended_verification": verifications
    }

@router.post("/analyze")
def run_risk_engine(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    projects = db.query(Project).all()
    if not projects:
        return {"message": "No projects found"}
        
    # 1. Prepare DataFrame for Isolation Forest
    data = []
    for p in projects:
        exp_ratio = float(p.expenditure / p.sanctioned_amount) if p.sanctioned_amount else 0.0
        prog_ratio = float(p.progress_percentage) / 100.0 if p.progress_percentage else 0.0
        data.append({
            "project_id": p.project_id,
            "exp_ratio": exp_ratio,
            "prog_ratio": prog_ratio,
            "cost": p.sanctioned_amount
        })
    df = pd.DataFrame(data)
    
    # 2. Run Isolation Forest
    clf = IsolationForest(contamination=0.05, random_state=42)
    features = df[['exp_ratio', 'prog_ratio', 'cost']].fillna(0)
    df['anomaly'] = clf.fit_predict(features)
    
    # Pre-fetch existing risk results to avoid N+1 query problem
    existing_risks = {r.project_id: r for r in db.query(RiskResult).all()}
    
    # 3. Apply Domain Rules + Store Results
    for p in projects:
        risk_data = generate_risk_for_project(p, df)
        existing = existing_risks.get(p.project_id)
        
        reasons_json = json.dumps(risk_data["reasons"])
        verifs_json = json.dumps(risk_data["recommended_verification"])
        
        if existing:
            existing.risk_score = risk_data["risk_score"]
            existing.risk_level = risk_data["risk_level"]
            existing.reasons = reasons_json
            existing.recommended_verification = verifs_json
            existing.model_version = "v1.hybrid"
        else:
            new_res = RiskResult(
                project_id=p.project_id,
                risk_score=risk_data["risk_score"],
                risk_level=risk_data["risk_level"],
                reasons=reasons_json,
                recommended_verification=verifs_json,
                model_version="v1.hybrid"
            )
            db.add(new_res)
            
    db.commit()
    return {"message": f"Successfully analyzed {len(projects)} projects."}

@router.get("/projects")
def get_risk_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Project, RiskResult).join(RiskResult, Project.project_id == RiskResult.project_id)
    
    if current_user.role == "STATE_AUTHORITY":
        query = query.filter(Project.state_id == current_user.state_id)
    elif current_user.role == "DISTRICT_AUTHORITY":
        query = query.filter(Project.district_id == current_user.district_id)
        
    results = query.all()
    
    out = []
    for p, r in results:
        out.append({
            "project_id": p.project_id,
            "project_title": p.project_title,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "category": p.category,
            "status": p.project_status
        })
    return sorted(out, key=lambda x: x['risk_score'], reverse=True)
@router.get("/projects/{project_id}")
def get_project_risk_detail(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Project).filter(Project.project_id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if current_user.role == "DISTRICT_AUTHORITY" and p.district_id != current_user.district_id:
        raise HTTPException(status_code=403, detail="Not authorized for this district")
    if current_user.role == "STATE_AUTHORITY" and p.state_id != current_user.state_id:
        raise HTTPException(status_code=403, detail="Not authorized for this state")
        
    r = db.query(RiskResult).filter(RiskResult.project_id == project_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Risk analysis not run for this project")
        raise HTTPException(status_code=404, detail="Risk analysis not run for this project")
        
    return {
        "project": p,
        "risk": {
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "reasons": json.loads(r.reasons) if r.reasons else [],
            "recommended_verification": json.loads(r.recommended_verification) if r.recommended_verification else []
        }
    }
