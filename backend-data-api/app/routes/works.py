from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.database import get_db
from app.models.transaction import Transaction
from app.models.work import Work
from app.schemas.transaction import TransactionOut
from app.schemas.work import WorkOut

router = APIRouter(prefix="/works", tags=["works"])


from app.models.constituency import Constituency

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
    works = query.offset(skip).limit(limit).all()
    
    results = []
    for w in works:
        c = db.query(Constituency).filter(Constituency.constituency_id == w.constituency_id).first()
        res = WorkOut.model_validate(w)
        res.projectId = f"WRK-{w.work_id}"
        res.project_id = f"WRK-{w.work_id}"
        res.sanctionedAmount = float(w.recommended_amount)
        res.constituency = c.name if c else "General Constituency"
        res.state = c.state if c else "National"
        res.riskScore = 55.0
        res.riskLevel = "MEDIUM"
        results.append(res)
    return results


@router.get("/{work_id}", response_model=WorkOut)
def get_work(work_id: str, db: Session = Depends(get_db)):
    work = None
    if work_id.isdigit():
        work = db.query(Work).filter(Work.work_id == int(work_id)).first()
    if not work:
        work = db.query(Work).filter(Work.title.contains(work_id)).first()
    if work is None:
        raise NotFoundError(detail=f"Work {work_id} not found")
    c = db.query(Constituency).filter(Constituency.constituency_id == work.constituency_id).first()
    res = WorkOut.model_validate(work)
    res.projectId = f"WRK-{work.work_id}"
    res.project_id = f"WRK-{work.work_id}"
    res.sanctionedAmount = float(work.recommended_amount)
    res.constituency = c.name if c else "General Constituency"
    res.state = c.state if c else "National"
    return res


@router.get("/{work_id}/transactions", response_model=list[TransactionOut])
def get_work_transactions(work_id: str, db: Session = Depends(get_db)):
    w_id = int(work_id) if work_id.isdigit() else 1
    return db.query(Transaction).filter(Transaction.work_id == w_id).all()

