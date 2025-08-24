from faststream import FastStream
from faststream.rabbit import RabbitBroker
from aiogram.types import InlineKeyboardMarkup
from loguru import logger
from typing import Dict, Any

from core.config import settings
from core.bot import bot
from keyboards.lessons import LessonKeyboards
from utils.formatters import format_lesson_info


class NotificationHandler:
    """Handles notifications from lesson-checker service"""
    
    def __init__(self):
        self.broker = RabbitBroker(settings.rabbit_url)
        self.app = FastStream(self.broker)
        
        # Register message handlers
        self.broker.subscriber(settings.NOTIFICATION_QUEUE)(self.handle_lesson_notification)
    
    async def handle_lesson_notification(self, message: Dict[str, Any]):
        """Handle lesson confirmation notification from lesson-checker"""
        try:
            if message.get("type") == "lesson_confirmation_required":
                await self._handle_confirmation_request(message)
            else:
                logger.warning(f"Unknown notification type: {message.get('type')}")
                
        except Exception as e:
            logger.error(f"Error handling notification: {e}")
    
    async def _handle_confirmation_request(self, message: Dict[str, Any]):
        """Handle lesson confirmation request"""
        try:
            lesson_id = message["lesson_id"]
            teacher_tg_id = message["teacher_tg_id"]
            student_name = message["student_name"]
            lesson_time = message["lesson_time"]
            
            # Format notification message
            text = (
                f"⏰ <b>Требуется подтверждение урока</b>\n\n"
                f"👤 <b>Студент:</b> {student_name}\n"
                f"📅 <b>Время урока:</b> {lesson_time}\n"
                f"🆔 <b>ID урока:</b> {lesson_id}\n\n"
                f"Урок начался более часа назад.\n"
                f"Пожалуйста, подтвердите - состоялся ли урок?"
            )
            
            # Create confirmation keyboard
            keyboard = LessonKeyboards.get_lesson_confirmation_keyboard(lesson_id)
            
            # Send notification to teacher
            await bot.send_message(
                chat_id=teacher_tg_id,
                text=text,
                reply_markup=keyboard
            )
            
            logger.info(f"Confirmation request sent for lesson {lesson_id} to teacher {teacher_tg_id}")
            
        except Exception as e:
            logger.error(f"Error sending confirmation request: {e}")
    
    async def start_listening(self):
        """Start listening for notifications"""
        try:
            await self.app.run()
        except Exception as e:
            logger.error(f"Error starting notification listener: {e}")
    
    async def stop_listening(self):
        """Stop listening for notifications"""
        try:
            await self.app.stop()
        except Exception as e:
            logger.error(f"Error stopping notification listener: {e}")


# Global notification handler instance
notification_handler = NotificationHandler()