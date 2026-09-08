from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base
from app.models import models
from app.routes import users, auth, cases


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SIH 2026 - Case Management API",
    description="Backend Case Management for Anomaly Investigation"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://civicshield-ops.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(cases.router)