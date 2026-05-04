import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(path="./chroma_db")

def get_collection(repo_name: str):
    return client.get_or_create_collection(
        name=repo_name,
        metadata={"hnsw:space": "cosine"}
    )

def store_chunks(repo_name: str, chunks: list[dict]):
    collection = get_collection(repo_name)
    collection.add(
        ids=[c['chunk_id'] for c in chunks],
        embeddings=[c['embedding'] for c in chunks],
        documents=[c['chunk_text'] for c in chunks],
        metadatas=[{
            'file_path': c['file_path'],
            'function_name': c['function_name'],
            'line_number': c['line_number'],
            'language': c['language']
        } for c in chunks]
    )

def search_chunks(repo_name: str, query_embedding: list[float], n_results: int = 20):
    collection = get_collection(repo_name)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results