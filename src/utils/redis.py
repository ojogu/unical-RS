# redis_client.py
import json
import redis.asyncio as redis
from typing import Optional
from src.utils.config import config
CACHE_TTL = 15  # 15 mins
REDIS_URL = config.redis_url

_redis: Optional[redis.Redis] = None

async def setup_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(REDIS_URL, decode_responses=True)
    return _redis

async def get_redis() -> redis.Redis:
    if _redis is None:
        raise RuntimeError("Redis has not been initialized. Call setup_redis() first.")
    return _redis


async def get_or_fetch_cache(
    key: str,
    fetch_callback: callable, # async function to fetch fresh data
    ttl: int = CACHE_TTL,
):
    redis = await get_redis()

    cached = await redis.get(key)
    if cached:
        return json.loads(cached)

    # If not found or expired, fetch new data
    fresh = await fetch_callback()
    await redis.set(key, json.dumps(fresh), ex=ttl)
    return fresh
