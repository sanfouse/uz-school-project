from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Redis настройки
    redis_host: str = "redis-master"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = "TVL9eZzcXs"
    
    # RabbitMQ настройки
    rabbitmq_host: str = "my-release-rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "user"
    rabbitmq_password: str = "buQcZ2hcVYK4yD2h"
    rabbitmq_queue: str = "scrapers"
    
    # Kubernetes настройки
    namespace: str = "default"
    k8s_timeout: int = 60
    k8s_labels: dict = {"scraper": "true"}
    
    # Scraper настройки
    scraper_image: str = "profi-scraper:latest"
    scraper_registry: str = "aadbccd8-cute-cygnus.registry.twcstorage.ru"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
