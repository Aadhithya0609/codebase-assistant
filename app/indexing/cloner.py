import git
import os
from pathlib import Path

SUPPORTED_EXTENSIONS = {'.py', '.js', '.ts', '.sql'}

def clone_repo(repo_url: str, target_dir: str) -> str:
    if os.path.exists(target_dir):
        repo = git.Repo(target_dir)
        repo.remotes.origin.pull()
        print(f"Pulled latest: {target_dir}")
    else:
        git.Repo.clone_from(repo_url, target_dir)
        print(f"Cloned: {repo_url}")
    return target_dir

def get_source_files(repo_dir: str) -> list[dict]:
    files = []
    skip_dirs = {'node_modules', '__pycache__', '.git', 'venv', 'dist', 'build'}
    
    for path in Path(repo_dir).rglob('*'):
        if any(skip in path.parts for skip in skip_dirs):
            continue
        if path.suffix not in SUPPORTED_EXTENSIONS:
            continue
        if path.is_file():
            files.append({
                'path': str(path),
                'language': path.suffix.lstrip('.'),
                'relative_path': str(path.relative_to(repo_dir))
            })
    
    return files

def get_file_hash(repo_dir: str, file_path: str) -> str:
    repo = git.Repo(repo_dir)
    relative = os.path.relpath(file_path, repo_dir)
    commits = list(repo.iter_commits(paths=relative, max_count=1))
    return commits[0].hexsha if commits else "unknown"