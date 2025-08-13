import playwright
from playwright.async_api import async_playwright, Browser as PlaywrightBrowser

from core.config import settings
from core.redis import client
from .browser import launch_browser

from core.logger import get_logger
from core.util import sleep_random_time
from core.broker import send_message
from src.orders.actions.accept import accept
from src.orders.actions.fetch import process_orders
from src.orders.actions.login import login


async def close_all_context(browser: PlaywrightBrowser):
    for ctx in browser.contexts:
        await ctx.close()


class Scraper:
    def __init__(self):
        self.is_running = True
        self.logger = get_logger(__name__, settings.log_level)

    async def run(self):
        await send_message(f"Scraper is running: {settings.profi_login}")
        async with async_playwright() as p:
            browser: PlaywrightBrowser = await launch_browser(p)
            context = await browser.new_context()

            order_page = await login(context)

            while self.is_running:
                try:
                    valid_orders = await process_orders(order_page)
                    response_limit = await client.get_response_limit()
                    if valid_orders and settings.accept and response_limit > 0:
                        await accept(context, valid_orders)
                    await sleep_random_time()
                except playwright.async_api.TimeoutError as ex:
                    self.logger.warning(
                        f"TimeoutError: close all context and login {ex}"
                    )
                    await close_all_context(browser)
                    context = await browser.new_context()
                    order_page = await login(context)
            await browser.close()

    async def stop(self):
        self.is_running = False
        self.logger.info("Scraper is stopping")
        await send_message(f"Scraper is closed: {settings.profi_login}")
