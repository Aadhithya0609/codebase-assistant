from app.indexing.cloner import clone_repo, get_source_files, get_file_hash
from app.indexing.parser import parse_file
from app.indexing.embedder import embed_text
from app.storage.chroma import store_chunks
from app.storage.redis_client import cache_get, cache_set
import uuid

def index_repo(repo_url: str, repo_name: str, target_dir: str):
    print(f"Starting indexing: {repo_url}")
    clone_repo(repo_url, target_dir)
    files = get_source_files(target_dir)
    print(f"Found {len(files)} files")

    all_chunks = []
    skipped = 0

    for file in files:
        file_hash = get_file_hash(target_dir, file['path'])
        cache_key = f"hash:{repo_name}:{file['relative_path']}"
        stored_hash = cache_get(cache_key)

        if stored_hash == file_hash:
            skipped += 1
            continue

        chunks = parse_file(file['path'], file['language'])

        for chunk in chunks:
            embedding = embed_text(chunk['chunk_text'])
            all_chunks.append({
                'chunk_id': str(uuid.uuid4()),
                'file_path': file['relative_path'],
                'function_name': chunk['function_name'],
                'line_number': chunk['line_number'],
                'language': file['language'],
                'chunk_text': chunk['chunk_text'],
                'embedding': embedding
            })

        cache_set(cache_key, file_hash, ttl=86400)

    if all_chunks:
        store_chunks(repo_name, all_chunks)
        print(f"Indexed {len(all_chunks)} chunks, skipped {skipped} unchanged files")
    else:
        print(f"Nothing new to index, skipped {skipped} files")