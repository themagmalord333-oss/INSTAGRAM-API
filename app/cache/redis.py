import redis.asyncio as redis
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger("redis")

class RedisCache:
    client: redis.Redis = None

    @classmethod
    async def connect(cls):
        pool = redis.ConnectionPool.from_url(
            settings.REDIS_URI, 
            max_connections=150, 
            decode_responses=True
        )
        cls.client = redis.Redis(connection_pool=pool)
        await cls.client.ping()
        logger.info("Redis Connection Pool Created.")

    @classmethod
    async def close(cls):
        if cls.client:
            await cls.client.close()

redis_client = RedisCache()