from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
    if not chunks:
        return []

    pairs = [[query, chunk["chunk_text"][:1000]] for chunk in chunks]

    try:
        scores = model.predict(pairs)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return [chunks[i] for i, score in ranked[:top_k]]
    except Exception as e:
        print(f"Reranker failed: {e}, falling back to semantic results")
        return chunks[:top_k]
