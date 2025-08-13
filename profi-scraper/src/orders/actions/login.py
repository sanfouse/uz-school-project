from playwright.async_api import BrowserContext, Page
from core.config import settings
from core.redis import client
from src.orders.page import PWPage, BACKOFFICE_URL, with_new_page


async def login(context: BrowserContext) -> Page:
    await _login(context)
    await _get_response_limit(context)

    order_page = await context.new_page()
    await order_page.goto(BACKOFFICE_URL)

    return order_page


@with_new_page
async def _login(page: PWPage) -> None:
    await page.login()


@with_new_page
async def _get_response_limit(page: PWPage) -> None:
    if settings.accept:
        response_limit = await page.update_response_limit()
        await client.update_response_limit(response_limit)

    return None
