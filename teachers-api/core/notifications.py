from datetime import datetime, timezone
from typing import Dict, Any, Optional
from faststream.rabbit import RabbitBroker
from loguru import logger
from core.config import settings


class NotificationService:
    def __init__(self, rabbitmq_url: str = None):
        from core.config import settings
        self.rabbitmq_url = rabbitmq_url or settings.rabbit_url
        self._broker = None
    
    async def get_broker(self) -> RabbitBroker:
        """Get or create RabbitMQ broker"""
        if self._broker is None:
            self._broker = RabbitBroker(self.rabbitmq_url)
            await self._broker.connect()
        return self._broker
    
    async def send_notification(self, message_text: str, teacher_id: Optional[int] = None):
        """Send formatted notification message to RabbitMQ"""
        try:
            broker = await self.get_broker()
            
            await broker.publish(
                message_text,
                settings.RABBIT_QUEUE
            )
            
            logger.info(f"Notification sent for teacher {teacher_id}")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    async def lesson_created(self, lesson_data: Dict[str, Any], teacher_id: int):
        """Notify about lesson creation"""
        message = f"🎯 <b>Новый урок создан</b>\n\n" \
                 f"👤 Ученик: {lesson_data.get('student_name')}\n" \
                 f"📅 Дата и время: {lesson_data.get('date_time')}\n" \
                 f"💰 Цена: {lesson_data.get('price')} руб\n" \
                 f"📝 Тип: {lesson_data.get('type')}\n" \
                 f"🆔 ID урока: {lesson_data.get('id')}"
        
        await self.send_notification(message, teacher_id)
    
    async def lesson_confirmed(self, lesson_data: Dict[str, Any], teacher_id: int):
        """Notify about lesson confirmation"""
        message = f"✅ <b>Урок подтвержден</b>\n\n" \
                 f"👤 Ученик: {lesson_data.get('student_name')}\n" \
                 f"📅 Дата и время: {lesson_data.get('date_time')}\n" \
                 f"💰 Цена: {lesson_data.get('price')} руб\n" \
                 f"🆔 ID урока: {lesson_data.get('id')}"
        
        await self.send_notification(message, teacher_id)
    
    async def lesson_cancelled(self, lesson_data: Dict[str, Any], teacher_id: int):
        """Notify about lesson cancellation"""
        message = f"❌ <b>Урок отменен</b>\n\n" \
                 f"👤 Ученик: {lesson_data.get('student_name')}\n" \
                 f"📅 Дата и время: {lesson_data.get('date_time')}\n" \
                 f"📝 Причина: {lesson_data.get('reason', 'Причина не указана')}\n" \
                 f"🆔 ID урока: {lesson_data.get('id')}"
        
        await self.send_notification(message, teacher_id)
    
    async def lesson_updated(self, lesson_data: Dict[str, Any], teacher_id: int, changes: Dict[str, Any]):
        """Notify about lesson update"""
        changes_text = "\n".join([f"• {key}: {value}" for key, value in changes.items()])
        message = f"✏️ <b>Урок обновлен</b>\n\n" \
                 f"👤 Ученик: {lesson_data.get('student_name')}\n" \
                 f"🆔 ID урока: {lesson_data.get('id')}\n\n" \
                 f"📝 <b>Изменения:</b>\n{changes_text}"
        
        await self.send_notification(message, teacher_id)
    
    async def invoice_paid(self, invoice_data: Dict[str, Any], teacher_id: int):
        """Notify about invoice payment"""
        message = f"💸 <b>Счет оплачен</b>\n\n" \
                 f"🧾 ID счета: {invoice_data.get('id')}\n" \
                 f"📚 ID урока: {invoice_data.get('lesson_id')}\n" \
                 f"💰 Сумма: {invoice_data.get('amount')} руб\n" \
                 f"📅 Дата оплаты: {datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M')}"
        
        await self.send_notification(message, teacher_id)
    
    async def teacher_registered(self, teacher_data: Dict[str, Any]):
        """Notify about teacher registration"""
        message = f"🎉 <b>Новый преподаватель зарегистрирован</b>\n\n" \
                 f"👨‍🏫 ФИО: {teacher_data.get('full_name')}\n" \
                 f"📧 Email: {teacher_data.get('email')}\n" \
                 f"🆔 Telegram ID: {teacher_data.get('tg_id')}\n" \
                 f"🆔 ID преподавателя: {teacher_data.get('id')}"
        
        await self.send_notification(message, teacher_data.get('id'))
    
    async def close(self):
        """Close broker connection"""
        if self._broker:
            await self._broker.stop()


# Global notification service instance
notification_service = NotificationService()