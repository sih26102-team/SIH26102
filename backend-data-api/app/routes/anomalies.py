from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.database import get_db
from app.models.anomaly import FlaggedAnomaly
from app.schemas.anomaly import AnomalyReviewIn, FlaggedAnomalyOut

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("", response_model=list[FlaggedAnomalyOut])
def list_anomalies(
    reviewed: str | None = Query(default=None),
    anomaly_type: str | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    List flagged anomalies, optionally filtered by review status
    (unreviewed/confirmed/dismissed) or anomaly_type.
    """
    query = db.query(FlaggedAnomaly)
    if reviewed is not None:
        query = query.filter(FlaggedAnomaly.reviewed == reviewed)
    if anomaly_type is not None:
        query = query.filter(FlaggedAnomaly.anomaly_type == anomaly_type)
    return query.offset(skip).limit(limit).all()


@router.get("/{anomaly_id}", response_model=FlaggedAnomalyOut)
def get_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    anomaly = db.query(FlaggedAnomaly).filter(FlaggedAnomaly.anomaly_id == anomaly_id).first()
    if anomaly is None:
        raise NotFoundError(detail=f"Anomaly {anomaly_id} not found")
    return anomaly


@router.patch("/{anomaly_id}/review", response_model=FlaggedAnomalyOut)
def review_anomaly(anomaly_id: int, payload: AnomalyReviewIn, db: Session = Depends(get_db)):
    """
    Mark a flagged anomaly as confirmed/dismissed. Who is allowed to call
    this is Poornesh's concern once auth is wired in front of this API —
    this layer only persists the review decision.
    """
    anomaly = db.query(FlaggedAnomaly).filter(FlaggedAnomaly.anomaly_id == anomaly_id).first()
    if anomaly is None:
        raise NotFoundError(detail=f"Anomaly {anomaly_id} not found")

    anomaly.reviewed = payload.reviewed
    anomaly.reviewed_by = payload.reviewed_by
    db.commit()
    db.refresh(anomaly)
    return anomaly
