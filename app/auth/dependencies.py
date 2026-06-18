from fastapi import Request, HTTPException, status
from app.core.cache import redis_client
from app.core.config import settings
import time

async def rate_limit_login(request: Request):
    # Use client IP as key; fallback to "unknown"
    client_ip = request.client.host if request.client else "unknown"
    key = f"login_rate:{client_ip}"
    current = await redis_client.get(key)
    if current and int(current) >= settings.LOGIN_RATE_LIMIT:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts")
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, settings.LOGIN_RATE_LIMIT_WINDOW)
    await pipe.execute()