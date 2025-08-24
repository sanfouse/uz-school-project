from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Bot Configuration
    TELEGRAM_BOT_TOKEN: str
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Teachers API Configuration
    TEACHERS_API_URL: str = "http://localhost:8080"
    TEACHERS_API_TIMEOUT: int = 30
    
    # RabbitMQ Configuration (for receiving notifications from lesson-checker)
    RABBIT_HOST: str = "localhost"
    RABBIT_PORT: int = 5672
    RABBIT_USER: str = "guest"
    RABBIT_PASSWORD: str = "guest"
    NOTIFICATION_QUEUE: str = "lesson_notifications"
    
    # Development
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def rabbit_url(self) -> str:
        return f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASSWORD}@{self.RABBIT_HOST}:{self.RABBIT_PORT}/"


settings = Settings()