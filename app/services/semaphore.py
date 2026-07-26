import time
import uuid
from app.cache.redis import redis_client

class TokenSemaphore:
    ACQUIRE_SCRIPT = """
    redis.call('zremrangebyscore', KEYS[1], '-inf', ARGV[1])
    if redis.call('zcard', KEYS[1]) < tonumber(ARGV[2]) then
        redis.call('zadd', KEYS[1], ARGV[3], ARGV[4])
        return 1
    else
        return 0
    end
    """

    @classmethod
    async def acquire(cls, key: str, limit: int, ttl: int = 30) -> str | None:
        now = time.time()
        expire_time = now + ttl
        token_id = str(uuid.uuid4())
        
        acquired = await redis_client.client.eval(
            cls.ACQUIRE_SCRIPT, 1, key, now, limit, expire_time, token_id
        )
        return token_id if acquired else None

    @classmethod
    async def release(cls, key: str, token_id: str):
        if token_id:
            await redis_client.client.zrem(key, token_id)