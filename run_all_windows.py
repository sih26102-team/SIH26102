from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
import asyncio
import os
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

client = httpx.AsyncClient()

@app.api_route('/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE'])
async def proxy(request: Request, path: str):
    if path.startswith('cases') or path.startswith('inspections') or path.startswith('audit'):
        target_url = f'http://127.0.0.1:8004/{path}'
    elif path.startswith('ml'):
        target_url = f'http://127.0.0.1:8002/{path.replace("ml/", "")}'
    else:
        target_url = f'http://127.0.0.1:8001/{path}'
    
    url = httpx.URL(target_url, query=request.url.query.encode('utf-8'))
    req = client.build_request(
        request.method,
        url,
        headers=request.headers.raw,
        content=await request.body()
    )
    try:
        resp = await client.send(req)
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        return Response(content=f"Proxy error: {str(e)}", status_code=502)

def start_services():
    print("Starting ML Engine (Port 8002)...")
    subprocess.Popen(["python", "-m", "uvicorn", "app.main:app", "--port", "8002"], cwd="ml-engine")
    
    print("Starting Backend Data API (Port 8001)...")
    subprocess.Popen(["python", "-m", "uvicorn", "app.main:app", "--port", "8001"], cwd="backend-data-api")
    
    print("Starting Backend Case Management (Port 8004)...")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath("backend-case-management")
    subprocess.Popen(["python", "-m", "uvicorn", "app.main:app", "--port", "8004"], cwd="backend-case-management", env=env)

if __name__ == '__main__':
    start_services()
    print("Starting Local API Gateway on http://localhost:8000 ...")
    uvicorn.run(app, host='127.0.0.1', port=8000)
