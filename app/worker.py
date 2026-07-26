from arq.connections import RedisSettings
from app.database.mongo import db_client
from app.services.fetcher import FetcherManager
from app.config.settings import settings

async def startup(ctx):
    await db_client.connect()

async def shutdown(ctx):
    await db_client.close()

async def background_refresh_profile(ctx, username: str):
    try:
        data = await FetcherManager.get_profile(username)
        await db_client.db.profiles.update_one(
            {"username": username}, {"$set": data}, upsert=True
        )
    except Exception:
        pass

class WorkerSettings:
    functions = [background_refresh_profile]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URI)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 50