import asyncio
from core.logger import get_logger
from src.orders.schema import Order
from core.redis import client
from src.orders.page import PWPage, with_new_page
from playwright.async_api import BrowserContext
from core.config import settings
from core.broker import send_message

logger = get_logger(__name__, settings.log_level)

MAX_CONCURRENT_PAGES = settings.mac_concurrent_pages


@with_new_page
async def _accept_order(page: PWPage, order: Order) -> bool:
    accepted, reason = await page.accept_order(order.link)
    if accepted:
        await send_message(order.get_message(accepted=accepted))
    else:
        await send_message(order.get_message(reason=reason))
    return accepted


async def _get_orders_to_process(
    orders: list[Order], response_limit: int
) -> list[Order]:
    return orders[:response_limit]


async def _process_orders(
    context: BrowserContext, orders: list[Order], semaphore: asyncio.Semaphore
) -> int:
    async def process_order(order: Order) -> bool:
        async with semaphore:
            return await _accept_order(context, order)

    tasks = [process_order(order) for order in orders]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return sum(1 for result in results if result is True)


async def _update_and_notify_response_limit(
    successful_accepts: int, current_limit: int
) -> None:
    new_limit = current_limit - successful_accepts
    await client.update_response_limit(new_limit)
    logger.info(f"Updated response limit: {new_limit}")
    await send_message(f"Оставшееся кол-во откликов: {new_limit}")


async def accept(context: BrowserContext, orders: list[Order]) -> None:
    response_limit = await client.get_response_limit()
    if response_limit <= 0:
        await send_message("Закончились комиссионные отклики")
        return

    orders_to_process = await _get_orders_to_process(orders, response_limit)
    logger.info(f"Processing {len(orders_to_process)} orders")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_PAGES)

    for i in range(0, len(orders_to_process), MAX_CONCURRENT_PAGES):
        batch = orders_to_process[i : i + MAX_CONCURRENT_PAGES]
        logger.info(f"Processing batch of {len(batch)} orders")
        successful_accepts = await _process_orders(context, batch, semaphore)
        await _update_and_notify_response_limit(successful_accepts, response_limit)
        response_limit -= successful_accepts
        if response_limit <= 0:
            await send_message("Закончились комиссионные отклики")
            break
