import sentry_sdk
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config.settings import settings
from app.middleware.security import EnterpriseMiddleware
from app.utils.exceptions import BaseAPIError
from app.database.mongo import db_client
from app.cache.redis import redis_client

from app.routers.v1 import profile # Import other routers similarly

if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=1.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    await redis_client.connect()
    yield
    await db_client.close()
    await redis_client.close()

app = FastAPI(title="Insta Public Web Backend", version="4.0.0", lifespan=lifespan)

@app.exception_handler(BaseAPIError)
async def custom_api_error_handler(request: Request, exc: BaseAPIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {"code": exc.code, "message": exc.message},
            "meta": {"request_id": getattr(request.state, "req_id", "unknown")}
        }
    )

app.add_middleware(EnterpriseMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app, include_in_schema=False)
app.include_router(profile.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "operational", "scale": "FAANG"}