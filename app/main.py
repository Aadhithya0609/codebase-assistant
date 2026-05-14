from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes.query import router as query_router
from app.api.routes.repo import router as repo_router
from celery_worker import celery_app
import os

app = FastAPI(
    title="Codebase Assistant",
    description="Ask questions about any codebase in plain English",
    version="1.0.0"
)

app.include_router(query_router)
app.include_router(repo_router)

os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return FileResponse("app/static/index.html")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/task/{task_id}")
async def task_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "ready": result.ready()
    }
