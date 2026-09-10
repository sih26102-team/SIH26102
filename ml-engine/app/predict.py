# predict.py — owner: Kousic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import os
import traceback

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
    sanctioned_amount: float = 0.0
    expenditure: float = 0.0
    amount: float | None = None
    progress_percent: float = 0.0
    transaction_id: int | str | None = None
    work_id: int | str | None = None

    class Config:
        extra = "allow"

def _run_inference(sanctioned: float, spent: float, progress: float) -> dict:
    burn_rate = spent / (progress + 1.0)
    input_df = pd.DataFrame([{
        'sanctioned_amount': sanctioned,
        'expenditure': spent,
        'progress_percent': progress,
        'burn_rate': burn_rate
    }])
    prediction = ml_engine.predict(input_df)[0] if ml_engine else 1
    risk_score = float(ml_engine.decision_function(input_df)[0]) if ml_engine else 0.0
    is_anomaly = True if prediction == -1 else False
    
    anomaly_type = "NORMAL"
    if is_anomaly:
        if spent > 0 and progress < 5.0:
            anomaly_type = "GHOST_PROJECT_RISK"
        elif progress > 0 and (spent / max(sanctioned, 1.0)) > (progress / 100.0) + 0.25:
            anomaly_type = "PROGRESS_SPEND_DIVERGENCE"
        else:
            anomaly_type = "UNUSUAL_BURN_RATE"

    return {
        "is_anomaly": is_anomaly,
        "prediction_code": int(prediction),
        "risk_score": risk_score,
        "score": round(float(abs(risk_score)), 4),
        "anomaly_type": anomaly_type
    }

@router.post("/")
@router.post("")
async def predict_anomaly(data: ProjectData):
    try:
        sanctioned = data.sanctioned_amount
        spent = data.expenditure if data.expenditure > 0 else (data.amount or 0.0)
        progress = data.progress_percent
        return _run_inference(sanctioned, spent, progress)
    except Exception as e:
        print("\n--- API ERROR TRACEBACK ---")
        traceback.print_exc()
        print("---------------------------\n")
        raise HTTPException(status_code=500, detail=str(e))

class BatchPayload(BaseModel):
    transactions: list[dict] = []

@router.post("/batch")
async def predict_batch(data: BatchPayload):
    try:
        results = []
        for item in data.transactions:
            sanctioned = float(item.get("sanctioned_amount", 0.0))
            spent = float(item.get("expenditure", item.get("amount", 0.0)))
            progress = float(item.get("progress_percent", 0.0))
            res = _run_inference(sanctioned, spent, progress)
            res["transaction_id"] = item.get("transaction_id")
            results.append(res)
        return {"results": results, "count": len(results)}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))