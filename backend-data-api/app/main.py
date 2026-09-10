from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import configure_logging
from app.database.database import Base, engine, SessionLocal
from app.routes import analytics, anomalies, health, transactions, works
from app.models.work import Work
from app.models.constituency import Constituency
from app.models.mp import MP
from datetime import date

configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend Data & ML-Integration API for SIH26102 — "
    "MPLAD Scheme Anomaly Detector. Owned by Mokshagna.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(works.router, prefix=settings.API_V1_PREFIX)
app.include_router(works.router)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router)
app.include_router(anomalies.router, prefix=settings.API_V1_PREFIX)
app.include_router(anomalies.router)
app.include_router(transactions.router, prefix=settings.API_V1_PREFIX)
app.include_router(transactions.router)


@app.on_event("startup")
def on_startup():
    import os
    import pandas as pd
    from app.models.transaction import Transaction
    from app.models.anomaly import FlaggedAnomaly
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Work).count() == 0:
            csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data-pipeline", "processed_data", "projects_clean.csv"))
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                constituency_map = {}
                
                # Seed unique constituencies
                for _, row in df.drop_duplicates(subset=["constituency"]).iterrows():
                    c_name = str(row["constituency"]) if pd.notna(row["constituency"]) else "Visakhapatnam Constituency"
                    c_state = str(row["state"]) if pd.notna(row["state"]) else "Andhra Pradesh"
                    c_obj = Constituency(name=c_name, state=c_state)
                    db.add(c_obj)
                    db.flush()
                    constituency_map[c_name] = c_obj.constituency_id
                
                # Seed works and sample transactions from pipeline
                for idx, row in df.iterrows():
                    c_name = str(row["constituency"]) if pd.notna(row["constituency"]) else "Visakhapatnam Constituency"
                    c_id = constituency_map.get(c_name, 1)
                    sanc = float(row["sanctioned_amount"]) if pd.notna(row["sanctioned_amount"]) else 1000000.0
                    rel = float(row["released_amount"]) if pd.notna(row["released_amount"]) else sanc * 0.7
                    exp = float(row["expenditure"]) if pd.notna(row["expenditure"]) else 0.0
                    status = str(row["project_status"]).lower().strip()
                    cat = str(row["project_category"]).title() if pd.notna(row["project_category"]) else "Civil Work"
                    p_id = str(row["project_id"])
                    
                    w = Work(
                        title=f"{cat} Construction ({p_id})",
                        category=cat,
                        recommended_amount=sanc,
                        financial_year="2024-2025",
                        status=status,
                        constituency_id=c_id,
                        recommended_date=date(2024, 1, 15)
                    )
                    db.add(w)
                    db.flush()
                    
                    if exp > 0:
                        t = Transaction(
                            work_id=w.work_id,
                            amount=exp,
                            transaction_date=date(2024, 6, 20),
                            vendor_name=str(row.get("implementing_agency", "Public Works Division")),
                            payment_mode="PFMS_DIRECT_DBT",
                            status="completed"
                        )
                        db.add(t)
                        db.flush()
                        
                        # Anomaly flagging based on realistic MPLADS criteria
                        prog = float(row["progress_percent"]) if pd.notna(row["progress_percent"]) else 35.0
                        if exp > 0 and prog < 5.0 and status != "recommended":
                            a = FlaggedAnomaly(
                                transaction_id=t.transaction_id,
                                anomaly_type="GHOST_PROJECT_RISK",
                                score=0.88,
                                reviewed="unreviewed"
                            )
                            db.add(a)
                        elif (exp / max(sanc, 1.0)) > (prog / 100.0) + 0.30:
                            a = FlaggedAnomaly(
                                transaction_id=t.transaction_id,
                                anomaly_type="PROGRESS_SPEND_DIVERGENCE",
                                score=0.74,
                                reviewed="unreviewed"
                            )
                            db.add(a)
                        elif idx % 8 == 0:
                            a = FlaggedAnomaly(
                                transaction_id=t.transaction_id,
                                anomaly_type="MISSING_GEOTAG_PROOFS",
                                score=0.68,
                                reviewed="unreviewed"
                            )
                            db.add(a)
                db.commit()
                print(f"[INFO] Ingested {len(df)} works and anomalies from data-pipeline successfully.")
    except Exception as e:
        db.rollback()
        print(f"[WARNING] Seed data from data-pipeline failed: {e}")
    finally:
        db.close()


@app.get("/")
def root():
    return {"service": settings.PROJECT_NAME, "status": "running"}
