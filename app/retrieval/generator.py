from groq import Groq
from app.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a senior software engineer helping a developer understand a codebase.
You will be given relevant code chunks from the codebase and a question.
Answer the question using ONLY the provided code chunks.
Always mention the exact file path and function name in your answer.
If the answer is not in the provided chunks, say so clearly. Never guess."""

def compress_chunks(chunks: list[dict], max_tokens_per_chunk: int = 500) -> str:
    context = ""
    for i, chunk in enumerate(chunks):
        text = chunk["chunk_text"][:max_tokens_per_chunk * 4]
        context += f"\n--- Chunk {i+1} ---\n"
        context += f"File: {chunk['file_path']}\n"
        context += f"Function: {chunk['function_name']}\n"
        context += f"Line: {chunk['line_number']}\n"
        context += f"Code:\n{text}\n"
    return context

def generate_answer(query: str, chunks: list[dict]) -> dict:
    context = compress_chunks(chunks)

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

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": [
            {
                "file_path": c["file_path"],
                "function_name": c["function_name"],
                "line_number": c["line_number"]
            }
            for c in chunks
        ]
    }
