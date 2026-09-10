# explain.py — owner: Kousic
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/explain", tags=["Explanation"])

class ExplainData(BaseModel):
    sanctioned_amount: float
    expenditure: float
    progress_percent: float = 0.0
    delay_days: int = 0
    missing_geotag: bool = False
    missing_tpi: bool = False
    missing_bills: bool = False
    is_anomaly: bool = False

@router.post("/")
async def explain_flag(data: ExplainData):
    reasons = []
    
    if not data.is_anomaly:
        return {"reasons": ["Project metrics are within normal statutory boundaries. No irregularities detected."]}

    # Ghost Project Detection (High financial disbursement with near-zero physical execution)
    if data.expenditure > 0 and data.progress_percent < 5.0:
        reasons.append("GHOST PROJECT RISK: Substantial financial disbursement recorded alongside near-zero (<5%) verified physical progress.")
        
    # Statutory Timeline & SLA Overrun (MPLADS Para 3.2.12 - 1-year completion limit)
    if data.delay_days > 180 or (data.progress_percent < 50.0 and data.delay_days > 90):
        reasons.append(f"STATUTORY SLA BREACH: Work is overdue by {data.delay_days} days beyond the 365-day statutory completion deadline (Para 3.2.12).")

    # Missing Deliverables & Compliance Documentation
    if data.missing_geotag:
        reasons.append("MISSING GEOTAG PROOF: Mandatory geo-tagged, timestamped site photographs not uploaded on eSAKSHI for reported physical progress.")

    if data.missing_tpi:
        reasons.append("MISSING TPI AUDIT: Mandatory Third-Party Inspection (TPI) report not submitted prior to fund clearance (Para 4.7).")

    if data.missing_bills:
        reasons.append("DOCUMENTATION DEFICIT: Itemized contractor measurement book (MB) bills and Utilisation Certificates (UC) not submitted.")

    # Contextual Siphoning & High Burn Rate Divergence
    burn_rate = data.expenditure / (data.progress_percent + 1.0)
    if data.progress_percent > 0 and (data.expenditure / max(data.sanctioned_amount, 1.0)) > (data.progress_percent / 100.0) + 0.30:
        reasons.append(f"PROGRESS-SPEND DIVERGENCE: Financial release is >30% ahead of on-site physical progress (Burn rate: ₹{burn_rate:,.2f} per 1% progress).")

    if len(reasons) == 0:
        reasons.append("AI ANOMALY: Statistical deviation in milestone progression velocity and fund withdrawal patterns flagged for supervisory inspection.")

    return {"reasons": reasons}