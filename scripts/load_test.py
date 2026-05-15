import threading
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_concurrent_queries(num_requests=50):
    """Send 50 questions simultaneously — does the API hold?"""
    results = []
    errors = []

    def send_query(i):
        try:
            start = time.time()
            res = requests.post(f"{BASE_URL}/query", json={
                "repo_name": "flask",
                "question": f"how does Flask handle routing request {i}"
            }, timeout=30)
            elapsed = time.time() - start
            results.append({
                "request": i,
                "status": res.status_code,
                "cached": res.json().get("cached", False),
                "time": round(elapsed, 2)
            })
        except Exception as e:
            errors.append({"request": i, "error": str(e)})

    print(f"Sending {num_requests} simultaneous queries...")
    threads = [threading.Thread(target=send_query, args=(i,)) for i in range(num_requests)]

    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total = time.time() - start

    print(f"\nResults:")
    print(f"  Total requests: {num_requests}")
    print(f"  Successful: {len(results)}")
    print(f"  Failed: {len(errors)}")
    print(f"  Total time: {round(total, 2)}s")
    if results:
        times = [r["time"] for r in results]
        cached = sum(1 for r in results if r["cached"])
        print(f"  Avg response time: {round(sum(times)/len(times), 2)}s")
        print(f"  Fastest: {min(times)}s")
        print(f"  Slowest: {max(times)}s")
        print(f"  Cached responses: {cached}/{len(results)}")
    if errors:
        print(f"  Errors: {errors[:3]}")

def test_cache_effectiveness(num_requests=20):
    """Ask the same question repeatedly — does Redis cache kick in?"""
    question = "how does Flask handle routing?"
    times = []

    print(f"\nSending same question {num_requests} times...")
    for i in range(num_requests):
        start = time.time()
        res = requests.post(f"{BASE_URL}/query", json={
            "repo_name": "flask",
            "question": question
        }, timeout=30)
        elapsed = time.time() - start
        cached = res.json().get("cached", False)
        times.append(elapsed)
        print(f"  Request {i+1}: {round(elapsed, 2)}s {'[CACHED]' if cached else '[FRESH]'}")

    print(f"\nFirst request (no cache): {round(times[0], 2)}s")
    print(f"Average cached requests: {round(sum(times[1:])/len(times[1:]), 2)}s")
    print(f"Cache speedup: {round(times[0]/times[1], 1)}x faster")

def test_invalid_inputs():
    """Send bad inputs — does the API crash or handle gracefully?"""
    print("\nTesting invalid inputs...")
    tests = [
        {"repo_name": "", "question": "test"},
        {"repo_name": "nonexistent_repo_xyz", "question": "test"},
        {"repo_name": "flask", "question": ""},
        {"repo_name": "flask" * 100, "question": "test"},
    ]

    for i, payload in enumerate(tests):
        try:
            res = requests.post(f"{BASE_URL}/query", json=payload, timeout=10)
            print(f"  Test {i+1}: status={res.status_code}")
        except Exception as e:
            print(f"  Test {i+1}: ERROR — {e}")

def test_celery_under_load(num_repos=5):
    """Submit multiple indexing jobs simultaneously"""
    print(f"\nSubmitting {num_repos} indexing jobs simultaneously...")
    repos = [
        ("https://github.com/pallets/flask", f"flask_load_{i}")
        for i in range(num_repos)
    ]

    task_ids = []
    for url, name in repos:
        res = requests.post(f"{BASE_URL}/repo/add", json={
            "repo_url": url,
            "repo_name": name
        })
        task_id = res.json().get("task_id", "").strip()
        task_ids.append(task_id)
        print(f"  Submitted: {name} → task {task_id[:8]}...")

    print("\nChecking task statuses after 5 seconds...")
    time.sleep(5)
    for task_id in task_ids:
        res = requests.get(f"{BASE_URL}/task/{task_id}")
        data = res.json()
        print(f"  Task {task_id[:8]}: {data['status']}")

if __name__ == "__main__":
    print("=" * 50)
    print("CODEBASE ASSISTANT — LOAD TEST")
    print("=" * 50)
    test_cache_effectiveness(10)
    test_invalid_inputs()
    test_concurrent_queries(20)
    test_celery_under_load(3)