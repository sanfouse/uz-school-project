from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    token: str
    chat_id: str

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 1
    redis_password: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
