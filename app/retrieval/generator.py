from groq import Groq
from app.config import GROQ_API_KEY
from app.retrieval.compressor import compress_chunks, fits_in_context

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a senior software engineer helping a developer understand a codebase.
Answer the question using ONLY the provided code chunks.
Always mention the exact file path and function name in your answer.
If the answer is not in the provided chunks, say so clearly. Never guess."""

def build_context(chunks: list[dict]) -> str:
    compressed = compress_chunks(chunks, max_chars_per_chunk=2000)
    fitted = fits_in_context(compressed, max_total_chars=8000)
    context = ""
    for i, chunk in enumerate(fitted):
        context += "\n--- Chunk " + str(i+1) + " ---\n"
        context += "File: " + chunk["file_path"] + "\n"
        context += "Function: " + chunk["function_name"] + "\n"
        context += "Line: " + str(chunk["line_number"]) + "\n"
        context += "Code:\n" + chunk["chunk_text"] + "\n"
    return context

def generate_answer(query: str, chunks: list[dict]) -> dict:
    context = build_context(chunks)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Code context:\n" + context + "\n\nQuestion: " + query}
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024,
        temperature=0.1
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [
            {
                "file_path": c["file_path"],
                "function_name": c["function_name"],
                "line_number": c["line_number"]
            }
            for c in chunks
        ]
    }