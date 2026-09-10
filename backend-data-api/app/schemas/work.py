from datetime import date
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict


class WorkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    work_id: int | str
    title: str
    category: str | None = None
    recommended_amount: Decimal | float = 0.0
    sanctionedAmount: float | None = None
    sanctioned_amount: float | None = None
    financial_year: str = "2024-2025"
    status: str = "ongoing"
    constituency_id: int | str | None = 1
    constituency: str | None = None
    district: str | None = None
    state: str | None = None
    recommended_date: date | None = None
    projectId: str | None = None
    project_id: str | None = None
    expenditure: float | None = None
    progressPercent: float | None = None
    progress_percent: float | None = None
    utilizationPct: float | None = None
    riskScore: float | None = None
    risk_score: float | None = None
    riskLevel: str | None = None
    risk_level: str | None = None
    delayDays: int | None = None
    delay_days: int | None = None
    reasons: list[Any] | None = None
    flags: list[Any] | None = None
