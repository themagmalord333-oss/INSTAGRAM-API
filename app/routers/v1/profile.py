import time
from fastapi import APIRouter, Request, Query
from app.services.orchestrator import get_profile_data
from app.utils.filters import filter_profile_data
from arq import create_pool
from arq.connections import RedisSettings
from app.config.settings import settings

router = APIRouter(tags=["Unified API"])
arq_redis = None

@router.on_event("startup")
async def startup():
    global arq_redis
    arq_redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URI))

@router.get("/profile")
async def get_unified_profile(
    request: Request,
    username: str,
    fields: str = Query("all")
):
    start_time = time.time()
    
    raw_data, source = await get_profile_data(username, arq_redis)
    process_time = f"{round((time.time() - start_time) * 1000, 2)}ms"
    
    full_payload = {
        "username": raw_data["username"],
        "profile": {
            "name": raw_data.get("full_name"),
            "bio": raw_data.get("biography"),
            "followers": raw_data.get("followers", 0),
        },
        "media": {
            "profile_picture": raw_data.get("profile_picture")
        },
        "meta": {
            "source": source,
            "cached": "cache" in source,
            "response_time": process_time,
            "request_id": getattr(request.state, "req_id", "unknown")
        }
    }
    
    return {"success": True, "data": filter_profile_data(full_payload, fields)}