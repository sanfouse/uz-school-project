from bs4 import BeautifulSoup
from src.orders.schema import Order


class Selector:
    def __init__(self, html: str):
        self.soup: BeautifulSoup = BeautifulSoup(html, "html.parser")

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

    def get_orders(self) -> list[Order]:
        orders = list()
        for container in self.containers:
            href = container.select_one(".SnippetBodyStyles__Container-sc-tnih0-2")[
                "href"
            ]
            order = Order(
                id=container.select_one(".SnippetBodyStyles__Container-sc-tnih0-2")[
                    "id"
                ],
                link=f"https://profi.ru{href}",
                subject=container.select_one(
                    ".SubjectAndPriceStyles__SubjectsText-sc-18v5hu8-1"
                ).text.strip(),
                description=container.select_one(
                    ".SnippetBodyStyles__MainInfo-sc-tnih0-6"
                ).text.strip(),
                price=container.select_one(
                    ".SubjectAndPriceStyles__PriceValue-sc-18v5hu8-5"
                ).text.strip(),
                time_info=container.select_one(
                    ".Date__DateText-sc-e1f8oi-1"
                ).text.strip(),
                client_name=container.select_one(
                    ".StatusAndClientInfoStyles__Name-sc-xp6j2r-9"
                ).text.strip(),
            )
            orders.append(order)
        return orders
