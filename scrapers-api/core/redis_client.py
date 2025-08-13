import json
from redis.asyncio import Redis
from .config import settings


async def save_scraper_config(job_id: str, config: dict):
    """Save scraper config to Redis with TTL."""
    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
        decode_responses=True,
    )
    try:
        await redis_client.setex(
            name=f"scraper:config:{job_id}", time=3600, value=json.dumps(config)
        )
    finally:
        await redis_client.close()
