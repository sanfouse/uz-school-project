import json
import asyncio
from datetime import datetime
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
    
    async def send_notification(self, event_type: str, data: Dict[str, Any], teacher_id: Optional[int] = None):
        """Send notification to RabbitMQ"""
        try:
            broker = await self.get_broker()
            
            message = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "teacher_id": teacher_id,
                "data": data
            }
            
            await broker.publish(
                json.dumps(message, default=str),
                settings.RABBIT_QUEUE
            )
            
            logger.info(f"Notification sent: {event_type} for teacher {teacher_id}")
            
        except Exception as e:
            logger.error(f"Failed to send notification {event_type}: {e}")
    
    async def lesson_created(self, lesson_data: Dict[str, Any], teacher_id: int):
        """Notify about lesson creation"""
        await self.send_notification(
            "lesson_created",
            {
                "lesson_id": lesson_data.get("id"),
                "student_name": lesson_data.get("student_name"),
                "date_time": lesson_data.get("date_time"),
                "price": lesson_data.get("price"),
                "type": lesson_data.get("type")
            },
            teacher_id
        )
    
    async def lesson_confirmed(self, lesson_data: Dict[str, Any], teacher_id: int):
        """Notify about lesson confirmation"""
        await self.send_notification(
            "lesson_confirmed",
            {
                "lesson_id": lesson_data.get("id"),
                "student_name": lesson_data.get("student_name"),
                "date_time": lesson_data.get("date_time"),
                "price": lesson_data.get("price")
            },
            teacher_id
        )
    
    async def lesson_cancelled(self, lesson_data: Dict[str, Any], teacher_id: int):
        """Notify about lesson cancellation"""
        await self.send_notification(
            "lesson_cancelled",
            {
                "lesson_id": lesson_data.get("id"),
                "student_name": lesson_data.get("student_name"),
                "date_time": lesson_data.get("date_time"),
                "reason": lesson_data.get("reason", "No reason provided")
            },
            teacher_id
        )
    
    async def lesson_updated(self, lesson_data: Dict[str, Any], teacher_id: int, changes: Dict[str, Any]):
        """Notify about lesson update"""
        await self.send_notification(
            "lesson_updated",
            {
                "lesson_id": lesson_data.get("id"),
                "student_name": lesson_data.get("student_name"),
                "changes": changes
            },
            teacher_id
        )
    
    async def invoice_paid(self, invoice_data: Dict[str, Any], teacher_id: int):
        """Notify about invoice payment"""
        await self.send_notification(
            "invoice_paid",
            {
                "invoice_id": invoice_data.get("id"),
                "lesson_id": invoice_data.get("lesson_id"),
                "amount": invoice_data.get("amount"),
                "payment_date": datetime.utcnow().isoformat()
            },
            teacher_id
        )
    
    async def teacher_registered(self, teacher_data: Dict[str, Any]):
        """Notify about teacher registration"""
        await self.send_notification(
            "teacher_registered",
            {
                "teacher_id": teacher_data.get("id"),
                "full_name": teacher_data.get("full_name"),
                "email": teacher_data.get("email"),
                "tg_id": teacher_data.get("tg_id")
            },
            teacher_data.get("id")
        )
    
    async def close(self):
        """Close broker connection"""
        if self._broker:
            await self._broker.close()


# Global notification service instance
notification_service = NotificationService()