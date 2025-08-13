from pydantic import BaseModel


class ScraperConfig(BaseModel):
    profi_login: str
    profi_password: str

    accept_text: str
    accept_price: str | None = None

    accept_newbie: str = "True"
    accept: str = "True"

    max_concurrent_pages: str = "3"

    proxy_host: str | None = None
    proxy_user: str | None = None
    proxy_password: str | None = None
    proxy_port: str | None = None
