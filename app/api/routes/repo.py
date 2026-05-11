from fastapi import APIRouter
from pydantic import BaseModel
from app.indexing.tasks import index_repo
import threading

router = APIRouter()

class RepoRequest(BaseModel):
    repo_url: str
    repo_name: str

class RepoResponse(BaseModel):
    message: str
    repo_name: str
    status: str

@router.post("/repo/add", response_model=RepoResponse)
async def add_repo(request: RepoRequest):
    target_dir = f"/tmp/repos/{request.repo_name}"
    thread = threading.Thread(
        target=index_repo,
        args=(request.repo_url, request.repo_name, target_dir)
    )
    thread.daemon = True
    thread.start()
    return {
        "message": "Indexing started in background",
        "repo_name": request.repo_name,
        "status": "indexing"
    }
