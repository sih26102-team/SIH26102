from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class WorkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    work_id: int
    title: str
    category: str | None = None
    recommended_amount: Decimal
    financial_year: str
    status: str
    constituency_id: int
    recommended_date: date | None = None
