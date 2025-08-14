import random
import json
import os
import asyncio

from core.broker import send_message
from core.config import settings
from core.logger import get_logger

from datetime import datetime, timedelta
from src.orders.schema import Order

logger = get_logger(__name__)

months = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


def check_input_date(date_str: str) -> bool:
    date_str = date_str.strip().lstrip("с ").strip()

    parts = date_str.split()

    if len(parts) == 2:
        day, month = int(parts[0]), months[parts[1]]
        year = datetime.today().year
    elif len(parts) == 3:
        day, month = int(parts[0]), months[parts[1]]
        year = int(parts[2])
    else:
        raise ValueError(f"Неверный формат даты: {date_str}")

    input_date = datetime(year, month, day).date()
    yesterday = datetime.today().date() - timedelta(days=1)

    return input_date >= yesterday


async def sleep_random_time():
    duration = random.randint(settings.page_refresh_min, settings.page_refresh_max)
    logger.debug(f"Sleeping {duration} seconds")
    await asyncio.sleep(duration)


def _load_words() -> list[str]:
    try:
        if os.path.exists("/app/config/words.json"):
            with open("/app/config/words.json") as f:
                words = json.load(f)
                return words if isinstance(words, list) else []
        else:
            return []
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        return []
