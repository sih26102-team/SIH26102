rom datetime import datetime

from pydantic import BaseModel, ConfigDict


class FlaggedAnomalyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    anomaly_id: int
    transaction_id: int
    anomaly_type: str
    score: float
    detected_at: datetime
    reviewed: str
    reviewed_by: str | None = None


class AnomalyReviewIn(BaseModel):
    reviewed: str  # "confirmed" | "dismissed"
    reviewed_by: str
