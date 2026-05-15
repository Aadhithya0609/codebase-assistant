from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.retrieval.searcher import hybrid_search
from app.retrieval.reranker import rerank
from app.retrieval.generator import generate_answer
from app.storage.redis_client import cache_get, cache_set
import json
import re

router = APIRouter()

class QueryRequest(BaseModel):
    repo_name: str
    question: str

class Source(BaseModel):
    file_path: str
    function_name: str
    line_number: int

class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    cached: bool = False

@router.post("/query", response_model=QueryResponse)
async def query_repo(request: QueryRequest):
    if not request.repo_name or not request.repo_name.strip():
        raise HTTPException(status_code=400, detail="repo_name cannot be empty")
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")
    if not re.match(r'^[a-zA-Z0-9._-]+$', request.repo_name):
        raise HTTPException(status_code=400, detail="repo_name contains invalid characters")

    cache_key = f"query:{request.repo_name}:{request.question.lower().strip()}"
    cached = cache_get(cache_key)
    if cached:
        data = json.loads(cached)
        data["cached"] = True
        return data

    chunks = hybrid_search(request.repo_name, request.question, n_results=20)
    reranked = rerank(request.question, chunks, top_k=5)
    result = generate_answer(request.question, reranked)

    cache_set(cache_key, json.dumps(result), ttl=3600)
    return {**result, "cached": False}