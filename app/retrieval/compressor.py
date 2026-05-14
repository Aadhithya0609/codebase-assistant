def compress_chunks(chunks: list[dict], max_chars_per_chunk: int = 2000) -> list[dict]:
    compressed = []
    for chunk in chunks:
        text = chunk["chunk_text"]
        if len(text) <= max_chars_per_chunk:
            compressed.append(chunk)
            continue
        lines = text.splitlines()
        kept = []
        total = 0
        for line in lines:
            if total + len(line) > max_chars_per_chunk:
                break
            kept.append(line)
            total += len(line)
        compressed.append({
            **chunk,
            "chunk_text": "\n".join(kept) + "\n... [truncated]"
        })
    return compressed

def fits_in_context(chunks: list[dict], max_total_chars: int = 8000) -> list[dict]:
    result = []
    total = 0
    for chunk in chunks:
        chunk_len = len(chunk["chunk_text"])
        if total + chunk_len > max_total_chars:
            break
        result.append(chunk)
        total += chunk_len
    return result