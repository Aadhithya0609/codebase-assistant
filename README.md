# Codebase Assistant

Ask questions about any GitHub repository in plain English. Get answers with exact file paths and line numbers.

## The Problem

You join a company. 50,000 lines of code. No documentation. Your manager says fix this bug by evening. You spend 3 hours just finding where the relevant code lives.

This tool solves that.

## How It Works

1. Point it at any GitHub repo
2. It parses every function using AST (not naive line splitting)
3. Converts each function into a semantic vector (embedding)
4. When you ask a question, it finds the most relevant functions using hybrid search
5. An LLM reads those functions and answers your question in plain English

## Architecture

Two pipelines:

**Indexing Pipeline** (runs once per repo, in background)
GitHub Repo → tree-sitter AST Parser → Embeddings → ChromaDB + PostgreSQL

**Query Pipeline** (runs on every question)
Question → Hybrid Search (Semantic + BM25) → Cross-Encoder Reranker → LLM → Answer + Citations

## Tech Stack

| Tool | Role |
|------|------|
| tree-sitter | AST-based code parsing |
| sentence-transformers | Local embeddings (no API cost) |
| ChromaDB | Vector storage and similarity search |
| PostgreSQL | Metadata storage (file path, function name, line number) |
| Redis | Query cache + file hash tracking |
| BM25 + Semantic | Hybrid search for better retrieval |
| Cross-encoder | Reranking top results before LLM call |
| Groq + LLaMA 3.3 70B | Fast, cheap LLM inference |
| FastAPI | REST API layer |
| Celery | Background job processing |

## API Endpoints

### Add a Repository
POST /repo/add
{
"repo_url": "https://github.com/pallets/flask",
"repo_name": "flask"
}

### Ask a Question
POST /query
{
"repo_name": "flask",
"question": "how does Flask handle routing?"
}

### Response
```json
{
  "answer": "Flask handles routing through...",
  "sources": [
    {
      "file_path": "src/flask/app.py",
      "function_name": "add_url_rule",
      "line_number": 987
    }
  ],
  "cached": false
}
```

## Setup

### Prerequisites
- Python 3.12+
- Docker Desktop
- WSL2 (Windows) or Linux/Mac

### Installation

```bash
git clone https://github.com/Aadhithya0609/codebase-assistant
cd codebase-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:
POSTGRES_URL=postgresql://aadhi:aadhi123@localhost:5432/codebase_assistant
REDIS_URL=redis://localhost:6380
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

### Start Databases
```bash
docker compose up -d
```

### Start Server
```bash
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the interactive API.

## Key Engineering Decisions

**Why AST parsing over line splitting?**
Naive line-based chunking breaks functions in half. tree-sitter extracts complete, meaningful units — one function = one chunk. The embedding captures the full intent.

**Why hybrid search?**
Semantic search alone misses exact function names. BM25 keyword search alone misses paraphrased questions. Hybrid with Reciprocal Rank Fusion gives both.

**Why reranking?**
Embedding similarity is a blunt instrument. A cross-encoder reads the query and chunk together and produces a precise relevance score. Drops top-20 to top-5 before the LLM call.

**Why Redis for file hashes?**
When a repo is updated, only changed files get re-indexed. A 500-file repo where 3 files changed takes 30 seconds, not 10 minutes. Indexing time is proportional to diff size, not repo size.

## Built By

Aadhi — targeting distributed systems engineering roles.
