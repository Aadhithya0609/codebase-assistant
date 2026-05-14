from celery_worker import celery_app
from app.indexing.tasks import index_repo as _index_repo

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def index_repo_task(self, repo_url: str, repo_name: str, target_dir: str):
    try:
        _index_repo(repo_url, repo_name, target_dir)
    except Exception as e:
        print(f"Task failed: {e}, retrying...")
        raise self.retry(exc=e)
