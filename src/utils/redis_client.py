# redis_client.py
import json
import redis.asyncio as redis
from typing import Optional
from src.utils.config import config

from src.utils.log import setup_logger
logger = setup_logger(__name__, "redis.log")

CACHE_TTL = 300
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


async def get_or_fetch_cache(key: str, fetch_callback, ttl: int = CACHE_TTL):
    try:
        redis = await get_redis()
        logger.debug(f"Attempting to get cached data for key: {key}")

        cached = await redis.get(key)
        if cached:
            logger.debug(f"Cache hit for key: {key}, value {cached}")
            return json.loads(cached)

        # fetch fresh data
        logger.debug("Cache miss, fetching fresh data...")
        fresh = await fetch_callback()
        logger.debug(f"Fetched fresh data: {fresh}")

        # set cache
        await redis.set(key, json.dumps(fresh), ex=ttl)

        # verify immediately
        verify = await redis.get(key)
        if not verify:
            logger.error(f"Key {key} failed to write to cache!")
            raise RuntimeError(f"Failed to cache data for key {key}")
        else:
            logger.debug(f"Key {key} written successfully and readable: {verify}")

        return fresh
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON for key {key}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in get_or_fetch_cache for key {key}: {str(e)}")
        raise

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
    
async def key_exist(key: str) -> bool:
    try:
        redis = await get_redis()
        exist = await redis.exists(key)
        logger.debug(f"Key {key} exists: {bool(exist)}")
        return bool(exist)
    except Exception as e:
        logger.error(f"Error checking if key {key} exists: {str(e)}")
        return False


async def get_from_cache(key: str):
    """
    Retrieve cached data for the given key.
    Returns the deserialized data if found, None otherwise.
    """
    try:
        redis = await get_redis()
        logger.debug(f"Attempting to get cached data for key: {key}")

        cached = await redis.get(key)
        if cached:
            logger.debug(f"Cache hit for key: {key}, value {cached}")
            return json.loads(cached)

        logger.debug(f"Cache miss for key: {key}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode cached JSON for key {key}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving cache for key {key}: {str(e)}")
        return None

async def clear_cache() -> bool:
    try:
        redis = await get_redis()
        await redis.flushdb()
        logger.info("Redis cache cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Error clearing Redis cache: {str(e)}")
        return False
