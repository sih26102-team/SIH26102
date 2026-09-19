from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import traceback
import joblib

router = APIRouter(prefix="/predict", tags=["Prediction"])

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "..", "models", "model.pkl")

ml_engine = None
try:
    if os.path.exists(model_path):
        ml_engine = joblib.load(model_path)
except Exception as e:
    print(f"Warning: Could not load model globally. {e}")

class ProjectData(BaseModel):
    project_id: str
    sanctioned_amount: float
    released_amount: float
    expenditure: float
    progress_percentage: float
    duration_days: float = 365.0

def _run_inference(project: ProjectData) -> dict:
    sanc = max(project.sanctioned_amount, 1.0)
    exp = project.expenditure
    prog = project.progress_percentage
    rel = project.released_amount

    # Feature Engineering
    spend_ratio = exp / sanc
    prog_ratio = prog / 100.0
    gap = spend_ratio - prog_ratio

    # 0-100 Risk Scoring Logic
    risk_score = 10.0 # Base risk
    signals = []

    # 1. High spend, low progress
    if gap > 0.25:
        risk_score += 40
        signals.append({
            "type": "PROGRESS_FINANCIAL_MISMATCH",
            "value": f"Spend is {spend_ratio*100:.1f}% but progress is only {prog:.1f}%",
            "explanation": "Financial expenditure significantly outpaces physical progress.",
            "severity": "HIGH"
        })
    elif gap > 0.10:
        risk_score += 20
        signals.append({
            "type": "PROGRESS_FINANCIAL_MISMATCH",
            "value": f"Spend {spend_ratio*100:.1f}%, Progress {prog:.1f}%",
            "explanation": "Financial expenditure is slightly ahead of physical progress.",
            "severity": "MEDIUM"
        })

    # 2. Ghost project risk (Spend > 0, Progress = 0)
    if exp > 0 and prog < 1.0:
        risk_score += 40
        signals.append({
            "type": "GHOST_PROJECT_RISK",
            "value": f"Spend: {exp}, Progress: {prog}%",
            "explanation": "Funds have been expended but no physical progress is reported.",
            "severity": "HIGH"
        })

    # 3. Unusually long duration
    if project.duration_days > 730 and prog < 100.0:
        risk_score += 20
        signals.append({
            "type": "UNUSUAL_DURATION",
            "value": f"{project.duration_days} days",
            "explanation": "Project has exceeded typical 2-year MPLADS expected completion timeline.",
            "severity": "MEDIUM"
        })
        
    # Cap score
    risk_score = min(risk_score, 100.0)

    # Risk Level mapping
    if risk_score >= 70:
        risk_level = "HIGH"
    elif risk_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "project_id": project.project_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "signals": signals,
        "recommended_verification": [
            "Verify expenditure records",
            "Verify physical progress on ground",
            "Review supporting records and bills",
            "Consider immediate field inspection"
        ] if risk_level == "HIGH" else []
    }

@router.post("")
@router.post("/")
async def predict_anomaly(data: ProjectData):
    try:
        return _run_inference(data)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class BatchPayload(BaseModel):
    projects: list[ProjectData]

@router.post("/batch")
async def predict_batch(data: BatchPayload):
    try:
        results = [_run_inference(p) for p in data.projects]
        return {"results": results, "count": len(results)}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))