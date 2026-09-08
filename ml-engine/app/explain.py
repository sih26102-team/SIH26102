# explain.py — owner: Kousic
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/explain", tags=["Explanation"])

class ExplainData(BaseModel):
    sanctioned_amount: float
    expenditure: float
    progress_percent: float = 0.0
    is_anomaly: bool

@router.post("/")
async def explain_flag(data: ExplainData):
    reasons = []
    
    if not data.is_anomaly:
        return {"reasons": ["Project metrics are within normal statistical boundaries. No action required."]}

    # Blatant Theft Detection
    if data.expenditure > data.sanctioned_amount:
        reasons.append(f"SEVERE: Expenditure (₹{data.expenditure}) explicitly exceeds the sanctioned budget (₹{data.sanctioned_amount}).")
        
    #Ghost Project Detection
    if data.expenditure > 0 and data.progress_percent < 5.0:
        reasons.append("GHOST PROJECT RISK: High financial expenditure detected alongside near-zero physical progress.")
        
    #Contextual Siphoning (AI Catch)
    burn_rate = data.expenditure / (data.progress_percent + 1.0)
    if len(reasons) == 0:
        reasons.append(f"AI ANOMALY: The mathematical burn rate (₹{burn_rate:,.2f} spent per 1% of progress) drastically violates normal government spending patterns.")

    return {"reasons": reasons}