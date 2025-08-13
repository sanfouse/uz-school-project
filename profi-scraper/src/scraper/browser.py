from playwright.async_api import Playwright, Browser as PlaywrightBrowser

from core.config import settings


async def launch_browser(playwright: Playwright) -> PlaywrightBrowser:
    proxy = None
    if settings.proxy_host:
        proxy = {
            "server": f"http://{settings.proxy_host}:{settings.proxy_port}",
            "username": settings.proxy_user,
            "password": settings.proxy_password,
        }
    return await playwright.chromium.launch(
        headless=settings.headless,
        proxy=proxy,
    )
