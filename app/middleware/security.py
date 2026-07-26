import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from app.config.settings import settings

class EnterpriseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.headers.get("content-length") and int(request.headers["content-length"]) > settings.MAX_REQUEST_SIZE:
            return JSONResponse(status_code=413, content={"error": "Payload too large"})

        req_id = str(uuid.uuid4())
        request.state.req_id = req_id 
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response