from sentence_transformers import SentenceTransformer
import threading

model = SentenceTransformer('all-MiniLM-L6-v2')
_lock = threading.Lock()

def embed_text(text: str) -> list[float]:
    text = text[:8000]
    with _lock:
        return model.encode(text).tolist()

def embed_batch(texts: list[str]) -> list[list[float]]:
    texts = [t[:8000] for t in texts]
    with _lock:
        return model.encode(texts).tolist()