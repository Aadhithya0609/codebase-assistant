from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text: str) -> list[float]:
    text = text[:8000]
    return model.encode(text).tolist()

def embed_batch(texts: list[str]) -> list[list[float]]:
    texts = [t[:8000] for t in texts]
    return model.encode(texts).tolist()