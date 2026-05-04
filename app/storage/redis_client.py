import redis
from app.config import REDIS_URL

client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def cache_set(key: str, value: str, ttl: int = 3600):
    client.set(key, value, ex=ttl)

def cache_get(key: str):
    return client.get(key)

def cache_delete_pattern(pattern: str):
    keys = client.keys(pattern)
    if keys:
        client.delete(*keys)