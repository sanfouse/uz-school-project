from bs4 import BeautifulSoup
from src.orders.schema import Order


class Selector:
    def __init__(self, html: str):
        self.soup: BeautifulSoup = BeautifulSoup(html, "html.parser")

    def _safe_text(self, element, default=""):
        """Безопасно извлекает текст из элемента"""
        if element is None:
            return default
        return element.text.strip() if element.text else default

    @property
    def containers(self):
        return self.soup.select(".OrderSnippetContainerStyles__Container-sc-1qf4h1o-0")

    @property
    def response_limit(self) -> int:
        element = self.soup.select_one(".Message__ResponseLimit-sc-1njfbi7-9")
        return int(element.text.strip()) if element else 0

    @property
    def order_user_info(self) -> dict:
        title_block = self.soup.select_one("span:-soup-contains('На Профи.ру')")
        created_at = None

        if title_block:
            parent = title_block.find_parent(
                class_="ClientSummaryBlock__Text-sc-17uaovi-2"
            )
            if parent:
                date_span = parent.select_one(
                    ".ClientSummaryBlock__Description-sc-17uaovi-4"
                )
                if date_span:
                    created_at = date_span.text.strip()

        reviews = self.soup.select(
            "div.styled__Container-sc-s63p74-0.fBVcag.Reviews__ReviewItem-sc-z9lvv3-2.hfuzQq"
        )

        return dict(created_at=created_at, reviews=len(reviews))

    @property
    def unviewed_messages(self) -> int | None:
        message_count = self.soup.select_one("div.global-badge.NavigationBarStyles__NavigationBarBadge-sc-qnnk0q-4.WYxvL")
        if message_count:
            int_message_count = int(message_count.text)
            return int_message_count if int_message_count > 0 else None
        return None

    def get_orders(self) -> list[Order]:
        orders = list()
        for container in self.containers:
            try:
                # Безопасно извлекаем href
                href_element = container.select_one(".SnippetBodyStyles__Container-sc-tnih0-2")
                if not href_element or not href_element.get("href"):
                    continue
                
                href = href_element["href"]
                
                order_id = href_element.get("id", "")
                
                subject = self._safe_text(
                    container.select_one(".SubjectAndPriceStyles__SubjectsText-sc-18v5hu8-1"),
                    "Без темы"
                )
                
                description = self._safe_text(
                    container.select_one(".SnippetBodyStyles__MainInfo-sc-tnih0-6"),
                    "Без описания"
                )
                
                price = self._safe_text(
                    container.select_one(".SubjectAndPriceStyles__PriceValue-sc-18v5hu8-5"),
                    "Цена не указана"
                )
                
                time_info = self._safe_text(
                    container.select_one(".Date__DateText-sc-e1f8oi-1"),
                    "Время не указано"
                )

                client_name = self._safe_text(
                    container.select_one(".StatusAndClientInfoStyles__Name-sc-xp6j2r-9.ihShvN")
                )
                
                order = Order(
                    id=order_id,
                    link=f"https://profi.ru{href}",
                    subject=subject,
                    description=description,
                    price=price,
                    time_info=time_info,
                    client_name=client_name
                )
                orders.append(order)
                
            except Exception as e:
                # Логируем ошибку и продолжаем
                print(f"Ошибка при обработке заказа: {e}")
                continue
                
        return orders
