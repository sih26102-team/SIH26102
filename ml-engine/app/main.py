# main.py — owner: Kousic
from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title = "SIH ML Engine API",
    description = "Machine Learning Engine for predictions and anamoly detection.",
    version="1.0.0"
   )
   
@app.get("/",tags=["Health"])
async def root():
    return {"message": "ML Engine server is running..."}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status":"healthy", "service":"ml-engine"}
    
    
if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
    