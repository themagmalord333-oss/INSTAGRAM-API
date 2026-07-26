from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger("mongo")

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(
            settings.MONGO_URI, 
            maxPoolSize=100, 
            minPoolSize=10
        )
        cls.db = cls.client[settings.MONGO_DB_NAME]
        await cls.db.profiles.create_index("username", unique=True)
        logger.info("MongoDB Connection Pool Created.")

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()

db_client = MongoDB()