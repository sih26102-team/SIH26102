# main.py — owner: Kousic
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app import predict, explain

app = FastAPI(
    title = "SIH ML Engine API",
    description = "Machine Learning Engine for predictions and anomaly detection.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

app.include_router(predict.router)
app.include_router(explain.router)

@app.get("/", tags=["Health"])
async def root():
    return {"message": "ML Engine server is running..."}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status":"healthy", "service":"ml-engine"}

if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
