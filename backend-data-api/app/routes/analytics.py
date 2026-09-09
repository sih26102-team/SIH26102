from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.anomaly import FlaggedAnomaly
from app.models.constituency import Constituency
from app.models.transaction import Transaction
from app.models.work import Work
from app.schemas.analytics import (
    AnalyticsSummary,
    AnomalyTypeBreakdown,
    ConstituencyAnomalyBreakdown,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(db: Session = Depends(get_db)):
    total_works = db.query(func.count(Work.work_id)).scalar() or 0
    total_transactions = db.query(func.count(Transaction.transaction_id)).scalar() or 0
    total_amount = db.query(func.coalesce(func.sum(Transaction.amount), 0)).scalar() or 0
    total_flagged = db.query(func.count(FlaggedAnomaly.anomaly_id)).scalar() or 0
    unreviewed = (
        db.query(func.count(FlaggedAnomaly.anomaly_id))
        .filter(FlaggedAnomaly.reviewed == "unreviewed")
        .scalar()
        or 0
    )

    return AnalyticsSummary(
        total_works=total_works,
        total_transactions=total_transactions,
        total_amount_disbursed=total_amount,
        total_flagged_anomalies=total_flagged,
        unreviewed_anomalies=unreviewed,
    )


@router.get("/by-constituency", response_model=list[ConstituencyAnomalyBreakdown])
def get_anomalies_by_constituency(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Constituency.constituency_id,
            Constituency.name.label("constituency_name"),
            func.count(FlaggedAnomaly.anomaly_id).label("flagged_count"),
            func.coalesce(func.sum(Transaction.amount), 0).label("total_flagged_amount"),
        )
        .join(Work, Work.constituency_id == Constituency.constituency_id)
        .join(Transaction, Transaction.work_id == Work.work_id)
        .join(FlaggedAnomaly, FlaggedAnomaly.transaction_id == Transaction.transaction_id)
        .group_by(Constituency.constituency_id, Constituency.name)
        .all()
    )

    return [
        ConstituencyAnomalyBreakdown(
            constituency_id=r.constituency_id,
            constituency_name=r.constituency_name,
            flagged_count=r.flagged_count,
            total_flagged_amount=r.total_flagged_amount,
        )
        for r in rows
    ]


@router.get("/by-anomaly-type", response_model=list[AnomalyTypeBreakdown])
def get_breakdown_by_anomaly_type(db: Session = Depends(get_db)):
    rows = (
        db.query(
            FlaggedAnomaly.anomaly_type,
            func.count(FlaggedAnomaly.anomaly_id).label("count"),
            func.avg(FlaggedAnomaly.score).label("avg_score"),
        )
        .group_by(FlaggedAnomaly.anomaly_type)
        .all()
    )

    return [
        AnomalyTypeBreakdown(anomaly_type=r.anomaly_type, count=r.count, avg_score=float(r.avg_score or 0))
        for r in rows
    ]

