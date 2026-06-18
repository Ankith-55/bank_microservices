import redis.asyncio as aioredis
from app.core.config import settings

redis_client = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    encoding="utf-8",
    decode_responses=True,
)

async def get_redis():
    return redis_client

async def cache_balance(account_number: str, balance: float):
    await redis_client.setex(
        f"balance:{account_number}",
        settings.REDIS_CACHE_TTL,
        str(balance)
    )

async def get_cached_balance(account_number: str) -> float | None:
    val = await redis_client.get(f"balance:{account_number}")
    return float(val) if val else None

async def invalidate_balance_cache(account_number: str):
    await redis_client.delete(f"balance:{account_number}")