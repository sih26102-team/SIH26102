from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import configure_logging
from app.database.database import Base, engine
from app.routes import analytics, anomalies, health, transactions, works

configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend Data & ML-Integration API for SIH26102 — "
    "MPLAD Scheme Anomaly Detector. Owned by Mokshagna.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENV == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(works.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(anomalies.router, prefix=settings.API_V1_PREFIX)
app.include_router(transactions.router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
def on_startup():
    if settings.ENV == "development":
        Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"service": settings.PROJECT_NAME, "status": "running"}

