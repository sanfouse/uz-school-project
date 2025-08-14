import json
from core.config import settings
from models.scraper_config import ScraperConfig


def make_env_vars(job_id: str, config: ScraperConfig) -> list[dict]:
    base_env = {
        "REDIS_HOST": settings.redis_host,
        "REDIS_PORT": str(settings.redis_port),
        "REDIS_DB": str(settings.redis_db),
        "REDIS_PASSWORD": settings.redis_password,
        "RABBITMQ_HOST": settings.rabbitmq_host,
        "RABBITMQ_PORT": str(settings.rabbitmq_port),
        "RABBITMQ_USER": settings.rabbitmq_user,
        "RABBITMQ_PASSWORD": settings.rabbitmq_password,
        "RABBITMQ_QUEUE": settings.rabbitmq_queue,
        "HEADLESS": "True",
        "LOG_LEVEL": "INFO",
        "JOB_ID": job_id,
    }

    scraper_env = config.model_dump(exclude_none=True)
    scraper_env = {k.upper(): v for k, v in scraper_env.items()}
    
    # Handle the words field specially - convert list to JSON string
    if "WORDS" in scraper_env:
        if scraper_env["WORDS"]:  # Only convert if the list is not empty
            scraper_env["WORDS"] = json.dumps(scraper_env["WORDS"], ensure_ascii=False)
        else:
            scraper_env["WORDS"] = "[]"  # Empty list as JSON string

    return [{"name": k, "value": v} for k, v in {**base_env, **scraper_env}.items()]
