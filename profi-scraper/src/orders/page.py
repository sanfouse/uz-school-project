import playwright.async_api
from playwright.async_api import Page

from core.config import settings
from core.logger import get_logger
from core.util import check_input_date
from .selector import Selector
from functools import wraps
from playwright.async_api import BrowserContext
from typing import Callable, TypeVar, Any

T = TypeVar("T")

RESPONSE_LIMIT_URL = "https://profi.ru/backoffice/a.php?action=stats&code=tml-stats"
BACKOFFICE_URL = "https://profi.ru/backoffice/"


class PWPage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(__name__, settings.log_level)
        self.logger.debug("Initializing Page object with default timeouts")
        self.page.set_default_navigation_timeout(1 * 60000)
        self.page.set_default_timeout(1 * 60000)

    async def login(self) -> None:
        self.logger.info("Attempting login to backoffice")
        try:
            self.logger.debug(f"Navigating to backoffice URL: {BACKOFFICE_URL}")
            await self.page.goto(BACKOFFICE_URL, wait_until="commit")
            await self.page.wait_for_selector(".login-form__input-login")
            self.logger.debug("Filling login form")
            await self.page.fill(".login-form__input-login", settings.profi_login)
            await self.page.fill(".login-form__input-password", settings.profi_password)
            self.logger.debug("Clicking login button")
            await self.page.click(".ui-button")
            self.logger.debug("Waiting for board grid container")
            await self.page.wait_for_selector("#BOARD_GRID_CONTAINER_ID")
            self.logger.info("Login successful")
        except playwright.async_api.TimeoutError as e:
            self.logger.error(f"Timeout during login: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {str(e)}")
            raise

    async def update_response_limit(self) -> int:
        self.logger.info("Fetching response limit page content")
        html = await self.get_response_limit_page_content()
        if html:
            self.logger.debug("Parsing response limit from HTML content")
            response_limit = Selector(html).response_limit
            self.logger.info(f"Response limit retrieved: {response_limit}")
            return response_limit
        self.logger.warning("No response limit content retrieved")
        return 0

    async def accept_order(self, order_url, client_name: str | None = "") -> tuple[bool, str]:
        self.logger.info(f"Attempting to accept order at URL: {order_url}")
        accepted = False
        reason = ""
        try:
            self.logger.debug(f"Navigating to order URL: {order_url}")
            await self.page.goto(order_url, wait_until="commit")

            opened = await self._click_open_order_popup()

            if opened:
                self.logger.debug("Order popup opened, waiting for order details")
                await self._wait_order_details_page()
                if await self.validate_client():
                    self.logger.debug("Client validated, filling order details")
                    accept_text = settings.accept_text.replace("__name__", client_name)
                    self.logger.debug(f"Accept text: {accept_text}")
                    await self._fill_order_details_text(accept_text)
                    await self._fill_price_details_text(settings.accept_price)
                    self.logger.debug("Attempting to accept order")
                    accepted = await self._click_accept_order()
                    if accepted:
                        self.logger.info("Order accepted successfully")
                    else:
                        self.logger.warning("Failed to accept order")
                        reason = "failed to click accept button"
                else:
                    self.logger.warning("Client validation failed: registered today")
                    reason = "client registered today"
            else:
                self.logger.warning("Failed to open order popup: no commission tariff")
                reason = "no commission tariff available"
        except Exception as e:
            self.logger.error(f"Error while accepting order: {str(e)}")
            reason = f"error: {str(e)}"
        return accepted, reason

    async def validate_client(self):
        self.logger.debug("Validating client information")
        try:
            html = await self.page.content()
            selector = Selector(html)
            created_at = selector.order_user_info["created_at"]
            self.logger.debug(f"Client creation date: {created_at}")
            if check_input_date(created_at) and not settings.accept_newbie:
                self.logger.info("Client is new and accept_newbie is disabled")
                return False
            self.logger.info("Client validation passed")
            return True
        except Exception as e:
            self.logger.error(f"Error during client validation: {str(e)}")
            return False

    async def _click_open_order_popup(self) -> bool:
        self.logger.debug("Attempting to open order popup")
        try:
            self.logger.debug("Waiting for tariff button")
            await self.page.wait_for_selector(
                "[class^='Tariffs__Button']"
            )

            lock_icon = self.page.locator(
                "svg[data-testid='orderCard/tariffs/lockIcon']"
            )
            if await lock_icon.is_visible():
                self.logger.warning("Lock icon visible, cannot proceed")
                return False

            self.logger.debug("Clicking commission tariff")
            await self.page.click('div:has(> div > span:text("Комиссия"))')
            self.logger.debug("Clicking tariff button")
            await self.page.click("[class^='Tariffs__Button']")
            self.logger.info("Order popup opened successfully")
            return True
        except playwright.async_api.TimeoutError:
            self.logger.error("Timeout while trying to open order popup")
            return False
        except Exception as e:
            self.logger.error(f"Error opening order popup: {str(e)}")
            return False

    async def get_response_limit_page_content(self) -> str | None:
        self.logger.info(f"Navigating to response limit page: {RESPONSE_LIMIT_URL}")
        try:
            await self.page.goto(RESPONSE_LIMIT_URL, wait_until="commit")
            self.logger.debug("Waiting for response limit selector")
            await self.page.wait_for_selector(
                "div[class^='Message__ResponseLimit']"
            )
            self.logger.debug("Retrieving page content")
            html = await self.page.content()
            self.logger.info("Response limit page content retrieved successfully")
            return html
        except playwright.async_api.TimeoutError:
            self.logger.error("Timeout while fetching response limit page content")
            return ""
        except Exception as e:
            self.logger.error(f"Error fetching response limit page content: {str(e)}")
            return ""

    async def _fill_order_details_text(self, text: str) -> None:
        self.logger.debug(f"Filling order details with text: {text}")
        try:
            await self.page.fill(
                'textarea[class*="TextAreaStyles__StyledTextArea"]',
                text,
            )
            self.logger.info("Order details text filled successfully")
        except Exception as e:
            self.logger.error(f"Error filling order details text: {str(e)}")
            raise

    async def _fill_price_details_text(self, text: str | None = "") -> None:
        if not text:
            text = ""
        self.logger.debug(f"Filling price details with text: {text}")
        try:
            await self.page.fill(
                'input[class*="backoffice-common-input__input"]',
                text,
            )
            self.logger.info("Price details text filled successfully")
        except Exception as e:
            self.logger.error(f"Error filling price details text: {str(e)}")
            raise

    async def _click_accept_order(self) -> bool:
        self.logger.debug("Attempting to click accept order button")
        try:
            await self.page.click('[class*="ButtonStyles__Container"][class*="PaymentMethodsFormStyles__ButtonWide"]')
            self.logger.info("Accept order button clicked successfully")
            return True
        except playwright.async_api.Error as e:
            self.logger.error(f"Error clicking accept order button: {str(e)}")
            return False

    async def _wait_order_details_page(self) -> None:
        self.logger.debug("Waiting for order details page to load")
        try:
            await self.page.wait_for_selector(
                ".order-card-bid-window-screen__body-content"
            )
            self.logger.info("Order details page loaded successfully")
        except playwright.async_api.TimeoutError:
            self.logger.error("Timeout waiting for order details page")
            raise
        except Exception as e:
            self.logger.error(f"Error waiting for order details page: {str(e)}")
            raise

    async def get_orders(self):
        await self.page.reload(timeout=1 * 60000, wait_until="commit")
        await self._wait_orders_in_page()
        html = await self.page.content()
        selector = Selector(html)
        return selector.get_orders()

    async def get_unviewed_messages(self) -> int | None:
        html = await self.page.content()
        selector = Selector(html)
        return selector.unviewed_messages

    async def _wait_orders_in_page(self):
        self.logger.debug("Waiting for orders in page")
        try:
            await self.page.wait_for_selector(
                ".OrderSnippetContainerStyles__Container-sc-1qf4h1o-0",
                timeout=1 * 10000,
            )
            self.logger.debug("Orders found in page")
        except playwright.async_api.TimeoutError:
            self.logger.warning("Timeout waiting for orders in page")
            return


def with_new_page(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    async def wrapper(context: BrowserContext, *args: Any, **kwargs: Any) -> T:
        page = PWPage(await context.new_page())
        try:
            result = await func(page, *args, **kwargs)
            return result
        finally:
            await page.page.close()

    return wrapper
