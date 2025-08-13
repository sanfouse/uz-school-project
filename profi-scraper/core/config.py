from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    clear_history_interval: int = 3600
    page_refresh_min: int = 5
    page_refresh_max: int = 15
    log_level: str | None = "INFO"
    admin_ids: str | None = ""
    service_url: str | None = "http://localhost:8000/api"

    rabbitmq_host: str = "localhost"
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_port: str = "5672"
    rabbitmq_queue: str = "scrapers"

    profi_login: str
    profi_password: str

    headless: bool = True
    proxy_host: str | None = None
    proxy_user: str | None = None
    proxy_password: str | None = None
    proxy_port: str | None = None

    page_refresh_min: int = 5
    page_refresh_max: int = 15
    accept: bool = True
    accept_text: str = """
    Здравствуйте!

Я не из тех, кто будет загружать вас скучной теорией и «таблицами времён». Вместо этого — разберёмся, что именно мешает вам в английском, и начнём говорить, понимать и думать на нём с первого же занятия.

Если готовы — предлагаю начать с короткой пробной встречи. Удобное время подскажете?
    """
    accept_price: str | None = None
    accept_newbie: bool = False

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 1
    redis_password: str | None = None

    mac_concurrent_pages: int = 5

    @property
    def admin_ids_list(self) -> list[int]:
        if not self.admin_ids:
            return []
        return [int(idx) for idx in self.admin_ids.split(",")]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
