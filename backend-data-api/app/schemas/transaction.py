from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: int
    work_id: int
    amount: Decimal
    transaction_date: date
    vendor_name: str | None = None
    payment_mode: str | None = None
    status: str


class TransactionWithAnomalyOut(TransactionOut):
    anomaly_score: float | None = None
    anomaly_type: str | None = None
