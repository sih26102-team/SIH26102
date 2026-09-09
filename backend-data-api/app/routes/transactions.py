from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.database import get_db
from app.models.anomaly import FlaggedAnomaly
from app.models.transaction import Transaction
from app.schemas.anomaly import FlaggedAnomalyOut
from app.services.ml_proxy import score_transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/{transaction_id}/score", response_model=FlaggedAnomalyOut)
def score_and_flag_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = (
        db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    )
    if transaction is None:
        raise NotFoundError(detail=f"Transaction {transaction_id} not found")

    payload = {
        "transaction_id": transaction.transaction_id,
        "work_id": transaction.work_id,
        "amount": float(transaction.amount),
        "transaction_date": transaction.transaction_date.isoformat(),
        "vendor_name": transaction.vendor_name,
        "payment_mode": transaction.payment_mode,
    }
    prediction = score_transaction(payload)

    anomaly = FlaggedAnomaly(
        transaction_id=transaction.transaction_id,
        anomaly_type=prediction.get("anomaly_type", "unknown"),
        score=prediction.get("score", 0.0),
    )
    db.add(anomaly)
    db.commit()
    db.refresh(anomaly)
    return anomaly
