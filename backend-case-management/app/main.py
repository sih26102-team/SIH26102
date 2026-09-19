from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.cases_router import router as cases_router
from app.routes.inspections_router import router as inspections_router
from app.routes.audit_router import router as audit_router

app = FastAPI(title='CivicShield AI - Case Management API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(cases_router)
app.include_router(inspections_router)
app.include_router(audit_router)

@app.get('/health')
def health_check():
    return {'status': 'ok'}
