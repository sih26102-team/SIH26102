from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.database import get_db
from app.models.transaction import Transaction
from app.models.work import Work
from app.schemas.transaction import TransactionOut
from app.schemas.work import WorkOut

router = APIRouter(prefix="/works", tags=["works"])


@router.get("", response_model=list[WorkOut])
def list_works(
    constituency_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Work)
    if constituency_id is not None:
        query = query.filter(Work.constituency_id == constituency_id)
    if status is not None:
        query = query.filter(Work.status == status)
    return query.offset(skip).limit(limit).all()


@router.get("/{work_id}", response_model=WorkOut)
def get_work(work_id: int, db: Session = Depends(get_db)):
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if work is None:
        raise NotFoundError(detail=f"Work {work_id} not found")
    return work


@router.get("/{work_id}/transactions", response_model=list[TransactionOut])
def get_work_transactions(work_id: int, db: Session = Depends(get_db)):
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if work is None:
        raise NotFoundError(detail=f"Work {work_id} not found")

    return db.query(Transaction).filter(Transaction.work_id == work_id).all()

