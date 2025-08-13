from redis.asyncio import Redis
from core.config import settings
from src.orders.schema import Order


class RedisClient:
    def __init__(self):
        self.client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True,
        )

    async def get_viewed_orders(self) -> set:
        return await self.client.smembers("viewed_orders") or set()

    async def get_response_limit(self) -> int:
        limit = await self.client.get("response_limit")
        return int(limit) if limit is not None else 0

    async def update_response_limit(self, limit: int) -> None:
        await self.client.set("response_limit", str(limit))

    async def add_viewed_orders(self, orders: list[Order]) -> None:
        for order in orders:
            await self.client.sadd("viewed_orders", order.id)


client = RedisClient()
