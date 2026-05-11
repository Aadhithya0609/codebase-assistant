from fastapi import FastAPI
from app.api.routes.query import router as query_router
from app.api.routes.repo import router as repo_router

app = FastAPI(
    title="Codebase Assistant",
    description="Ask questions about any codebase in plain English",
    version="1.0.0"
)

app.include_router(query_router)
app.include_router(repo_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
