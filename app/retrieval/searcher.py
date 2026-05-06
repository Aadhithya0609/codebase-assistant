from app.storage.chroma import search_chunks
from app.indexing.embedder import embed_text
from rank_bm25 import BM25Okapi

def semantic_search(repo_name: str, query: str, n_results: int = 20):
    query_embedding = embed_text(query)
    results = search_chunks(repo_name, query_embedding, n_results)

    chunks = []
    for i, doc in enumerate(results['documents'][0]):
        chunks.append({
            'chunk_text': doc,
            'file_path': results['metadatas'][0][i]['file_path'],
            'function_name': results['metadatas'][0][i]['function_name'],
            'line_number': results['metadatas'][0][i]['line_number'],
            'language': results['metadatas'][0][i]['language'],
            'score': 1 - results['distances'][0][i]
        })
    return chunks

def bm25_search(chunks: list[dict], query: str, n_results: int = 20):
    if not chunks:
        return []

    tokenized_corpus = [c['chunk_text'].lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    return [chunks[i] for i, score in ranked[:n_results]]

def hybrid_search(repo_name: str, query: str, n_results: int = 20):
    semantic_results = semantic_search(repo_name, query, n_results)

    if not semantic_results:
        return []

    bm25_results = bm25_search(semantic_results, query, n_results)

    seen = set()
    merged = []
    for chunk in bm25_results + semantic_results:
        key = chunk['function_name'] + chunk['file_path']
        if key not in seen:
            seen.add(key)
            merged.append(chunk)

    return merged[:n_results]
