# redis_client.py
import json
import redis.asyncio as redis
from typing import Optional
from src.utils.config import config

from src.utils.log import setup_logger
logger = setup_logger(__name__, "redis.log")

CACHE_TTL = 60 * 2  # 10 mins
REDIS_URL = config.redis_url

_redis: Optional[redis.Redis] = None

async def setup_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        # logger.info(f"Initializing Redis connection to {REDIS_URL}")
        try:
            _redis = redis.from_url(REDIS_URL, decode_responses=True)
            # logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {str(e)}")
            raise
    return _redis

async def get_redis() -> redis.Redis:
    if _redis is None:
        logger.error("Redis connection not initialized")
        raise RuntimeError("Redis has not been initialized. Call setup_redis() first.")
    return _redis


async def get_or_fetch_cache(key: str, fetch_callback: callable, ttl: int = CACHE_TTL):
    redis = await get_redis()
    logger.debug(f"Attempting to get cached data for key: {key}")

    cached = await redis.get(key)
    if cached:
        logger.debug(f"Cache hit for key: {key}, value {cached}")
        return json.loads(cached)

    # fetch fresh data
    logger.debug("catch miss.....")
    fresh = await fetch_callback()
    logger.debug(f"Fetched fresh data: {fresh}")

    # set cache
    await redis.set(key, json.dumps(fresh), ex=ttl)
    
    # verify immediately
    verify = await redis.get(key)
    if not verify:
        logger.error(f"Key {key} failed to write!")
        return
    else:
        logger.debug(f"Key {key} written successfully and readable: {verify}")

    return fresh

async def set_cache(key: str, data, ttl: int = CACHE_TTL) -> bool:
    """
    Store `data` (JSON-serializable) under `key` with expiration `ttl` seconds.
    Returns True on success, False on failure.
    """
    try:
        redis_conn = await get_redis()
        payload = json.dumps(data)
        await redis_conn.set(key, payload, ex=ttl)
        logger.debug(f"Set cache for key={key} ttl={ttl} payload={payload}")
        return True
    except Exception as e:
        logger.error(f"Failed to write cache for key {key}: {e}")
        return False
    
async def key_exist(key:str):
    redis = await get_redis()
    exist = await redis.exists(key)
    if exist:
        return True
    return False


async def get_from_cache(key: str):
    """
    Retrieve cached data for the given key.
    Returns the deserialized data if found, None otherwise.
    """
    redis = await get_redis()
    logger.debug(f"Attempting to get cached data for key: {key}")

    cached = await redis.get(key)
    if cached:
        logger.debug(f"Cache hit for key: {key}, value {cached}")
        return json.loads(cached)

    logger.debug(f"Cache miss for key: {key}")
    return None
