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
    sanctioned_amount: float
    expenditure: float
    progress_percent: float = 0.0

@router.post("/")
async def predict_anomaly(data: ProjectData):
    try:
        # Check if the global model loaded successfully
        if ml_engine is None:
            raise HTTPException(status_code=500, detail=f"Model not loaded on server. Check {model_path}")
            
        burn_rate = data.expenditure / (data.progress_percent + 1.0)
        
        input_df = pd.DataFrame([{
            'sanctioned_amount': data.sanctioned_amount,
            'expenditure': data.expenditure,
            'progress_percent': data.progress_percent,
            'burn_rate': burn_rate
        }])
        
        prediction = ml_engine.predict(input_df)[0]
        risk_score = ml_engine.decision_function(input_df)[0]
        
        return {
            "is_anomaly": True if prediction == -1 else False,
            "prediction_code": int(prediction),
            "risk_score": float(risk_score)
        }
    except Exception as e:
        print("\n--- API ERROR TRACEBACK ---")
        traceback.print_exc()
        print("---------------------------\n")
        raise HTTPException(status_code=500, detail=str(e))