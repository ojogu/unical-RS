# redis_client.py
import json
import redis.asyncio as redis
from typing import Optional
from src.utils.config import config

from src.utils.log import setup_logger
logger = setup_logger(__name__, "redis.log")

CACHE_TTL = 10 # 10 mins
REDIS_URL = config.redis_url

_redis: Optional[redis.Redis] = None

async def setup_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        logger.info(f"Initializing Redis connection to {REDIS_URL}")
        try:
            _redis = redis.from_url(REDIS_URL, decode_responses=True)
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {str(e)}")
            raise
    return _redis

async def get_redis() -> redis.Redis:
    if _redis is None:
        logger.error("Redis connection not initialized")
        raise RuntimeError("Redis has not been initialized. Call setup_redis() first.")
    return _redis

async def get_or_fetch_cache(
    key: str,
    fetch_callback: callable, # async function to fetch fresh data
    ttl: int = CACHE_TTL,
):
    redis = await get_redis()
    logger.debug(f"Attempting to get cached data for key: {key}")

    try:
        cached = await redis.get(key)
        if cached:
            logger.debug(f"Cache hit for key: {key}")
            return json.loads(cached)

        logger.debug(f"Cache miss for key: {key}, fetching fresh data")
        fresh = await fetch_callback()
        logger.debug(f"data before storing: {fresh}")
        str_data = json.dumps(fresh)
        await redis.set(key, str_data, ex=ttl)
        logger.debug(f"data after storing: {str_data}")
        logger.debug(f"Successfully cached new data for key: {key}")
        return fresh

    except Exception as e:
        logger.error(f"Error in cache operation for key {key}: {str(e)}")
        raise
