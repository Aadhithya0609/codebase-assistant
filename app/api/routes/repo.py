from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class RepoRequest(BaseModel):
    repo_url: str
    repo_name: str

class RepoResponse(BaseModel):
    message: str
    repo_name: str
    status: str
    task_id: str

@router.post("/repo/add", response_model=RepoResponse)
async def add_repo(request: RepoRequest):
    from app.indexing.celery_tasks import index_repo_task
    target_dir = f"/tmp/repos/{request.repo_name}"

    task = index_repo_task.delay(
        request.repo_url,
        request.repo_name,
        target_dir
    )

    return {
        "message": "Indexing started in background",
        "repo_name": request.repo_name,
        "status": "indexing",
        "task_id": task.id.strip()
    }
