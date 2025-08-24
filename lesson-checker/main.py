import asyncio
from datetime import datetime, timedelta, timezone
import logging
import sys
from typing import List

import asyncpg
from faststream.rabbit import RabbitBroker

from config import settings


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


DATABASE_URL = settings.database_url
RABBITMQ_URL = settings.rabbit_url
NOTIFICATION_QUEUE = "lesson_notifications"

broker = RabbitBroker(RABBITMQ_URL)


async def get_lessons_needing_confirmation(db_pool: asyncpg.Pool) -> List[dict]:
    """
    Получает уроки, которые начались более часа назад и требуют подтверждения
    """
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    
    query = """
    SELECT 
        l.id,
        l.student_name,
        l.date_time,
        l.price,
        l.type,
        t.full_name as teacher_name,
        t.tg_id as teacher_tg_id,
        t.email as teacher_email
    FROM lessons l
    JOIN teachers t ON l.teacher_id = t.id
    WHERE l.date_time <= $1
    AND l.status = 'planned' and l.type = 'regular'
    """
    
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(query, one_hour_ago)
        return [dict(row) for row in rows]


async def send_notification(lesson: dict):
    """
    Отправляет уведомление о необходимости подтверждения урока
    """
    message = {
        "type": "lesson_confirmation_required",
        "lesson_id": lesson["id"],
        "student_name": lesson["student_name"],
        "teacher_name": lesson["teacher_name"],
        "teacher_tg_id": lesson["teacher_tg_id"],
        "teacher_email": lesson["teacher_email"],
        "lesson_time": lesson["date_time"].isoformat(),
        "price": float(lesson["price"]),
        "message": f"Урок с {lesson['student_name']} начался более часа назад. Требуется подтверждение."
    }
    
    await broker.publish(message, NOTIFICATION_QUEUE)
    logger.info(f"Отправлено уведомление для урока {lesson['id']}")


async def check_lessons():
    """
    Основная функция проверки уроков
    """
    try:
        # Подключение к базе данных
        db_pool = await asyncpg.create_pool(DATABASE_URL)
        logger.info("Подключение к базе данных установлено")
        
        # Подключение к RabbitMQ
        await broker.start()
        logger.info("Подключение к RabbitMQ установлено")
        
        # Получаем уроки, требующие подтверждения
        lessons = await get_lessons_needing_confirmation(db_pool)
        logger.info(f"Найдено {len(lessons)} уроков, требующих подтверждения")
        
        # Отправляем уведомления для каждого урока
        for lesson in lessons:
            try:
                await send_notification(lesson)
                logger.info(f"Уведомление отправлено для урока {lesson['id']}")
            except Exception as e:
                logger.error(f"Ошибка при обработке урока {lesson['id']}: {e}")
        
        # Закрываем соединения
        await db_pool.close()
        await broker.stop()
        logger.info("Проверка уроков завершена успешно")
        
    except Exception as e:
        logger.error(f"Критическая ошибка при проверке уроков: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(check_lessons())
