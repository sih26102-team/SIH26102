from decimal import Decimal

from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_works: int
    total_transactions: int
    total_amount_disbursed: Decimal
    total_flagged_anomalies: int
    unreviewed_anomalies: int


class ConstituencyAnomalyBreakdown(BaseModel):
    constituency_id: int
    constituency_name: str
    flagged_count: int
    total_flagged_amount: Decimal


class AnomalyTypeBreakdown(BaseModel):
    anomaly_type: str
    count: int
    avg_score: float
