import asyncio
import json
from typing import Callable, Any
from app.cache.redis import redis_client
from app.utils.logger import get_logger

logger = get_logger("distributed_lock")

class DistributedSingleFlight:
    @staticmethod
    async def execute(username: str, fetch_coro: Callable, cache_ttl: int) -> dict:
        cache_key = f"ig:profile:{username}"
        lock_key = f"lock:ig:{username}"
        
        acquired = await redis_client.client.set(lock_key, "locked", nx=True, ex=15)
        
        if acquired:
            try:
                data = await fetch_coro(username)
                await redis_client.client.setex(cache_key, cache_ttl, json.dumps(data))
                return data
            finally:
                await redis_client.client.delete(lock_key)
        else:
            for _ in range(30):
                await asyncio.sleep(0.5)
                cached = await redis_client.client.get(cache_key)
                if cached:
                    return json.loads(cached)
            raise TimeoutError("Timeout waiting for data.")