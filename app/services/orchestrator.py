cat << 'EOF' > /home/ubuntu/INSTAAPI/app/services/orchestrator.py
from bson import json_util
from datetime import datetime, timezone
from app.cache.redis import redis_client
from app.database.mongo import db_client
from app.services.fetcher import FetcherManager
from app.services.distributed_lock import DistributedSingleFlight
from app.services.semaphore import TokenSemaphore
from app.config.settings import settings
from app.utils.exceptions import CapacityExceededError

async def get_profile_data(username: str, arq_queue) -> tuple[dict, str]:
    cache_key = f"ig:profile:{username}"
    await redis_client.client.incr("stats:total_searches")

    # 1. Fast Cache
    cached_redis = await redis_client.client.get(cache_key)
    if cached_redis:
        await redis_client.client.incr("stats:cache_hits")
        return json_util.loads(cached_redis), "cache_fast_redis"

    # 2. DB / Stale Cache
    db_record = await db_client.db.profiles.find_one({"username": username})
    if db_record:
        db_record.pop("_id", None)
        updated_at = db_record["updated_at"]
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
            
        age_seconds = (datetime.now(timezone.utc) - updated_at).total_seconds()
        if age_seconds < settings.FAST_CACHE_TTL:
            await redis_client.client.incr("stats:cache_hits")
            await redis_client.client.setex(cache_key, settings.FAST_CACHE_TTL, json_util.dumps(db_record))
            return db_record, "cache_fast_mongo"
        elif age_seconds < settings.STALE_CACHE_TTL:
            await redis_client.client.incr("stats:cache_hits")
            if arq_queue:
                await arq_queue.enqueue_job('background_refresh_profile', username)
            return db_record, "cache_stale_refreshing"

    # 3. Live Fetch 
    async def _fetch_and_save(u: str):
        token = await TokenSemaphore.acquire("semaphore:global_fetches", limit=100, ttl=30)
        if not token:
            raise CapacityExceededError()
            
        try:
            data = await FetcherManager.get_profile(u)
            data["updated_at"] = datetime.now(timezone.utc)
            await db_client.db.profiles.update_one({"username": u}, {"$set": data}, upsert=True)
            data["updated_at"] = data["updated_at"].isoformat()
            return data
        except Exception as e:
            await redis_client.client.incr("stats:errors")
            raise e
        finally:
            await TokenSemaphore.release("semaphore:global_fetches", token)

    live_data = await DistributedSingleFlight.execute(username, _fetch_and_save, settings.FAST_CACHE_TTL)
    return live_data, "live_fetch"
EOF