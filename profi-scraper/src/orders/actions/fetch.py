from playwright.async_api import Page

from core.config import settings
from core.logger import get_logger
from core.broker import send_messages
from core.redis import client
from src.orders.schema import Order
from src.orders.services import is_valid_order
from src.orders.page import PWPage

logger = get_logger(__name__, settings.log_level)


async def process_orders(page: Page):
    page = PWPage(page)

    orders = await page.get_orders()
    validated_orders = await _validate_orders(orders)

    orders_messages = [order.get_message() for order in validated_orders]
    await send_messages(orders_messages)

    await client.add_viewed_orders(validated_orders)

    return validated_orders


async def _validate_orders(orders: list[Order]):
    if not orders:
        logger.info(f"{settings.profi_login}: No containers found")
        return []

    viewed_orders = await client.get_viewed_orders()

    valid_orders = [
        order
        for order in orders
        if await is_valid_order(order) and order.id not in viewed_orders
    ]

    return valid_orders
