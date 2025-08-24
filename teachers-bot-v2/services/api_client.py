import httpx
from typing import Optional, List, Dict, Any
from loguru import logger
from pydantic import BaseModel

from core.config import settings


class APIError(Exception):
    """API communication error"""
    pass


class TeachersAPIClient:
    """Client for communicating with teachers-api"""
    
    def __init__(self):
        self.base_url = settings.TEACHERS_API_URL
        self.timeout = settings.TEACHERS_API_TIMEOUT
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"API request failed: {method} {url} - {e}")
                raise APIError(f"API request failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in API request: {e}")
                raise APIError(f"Unexpected error: {e}")
    
    # Teacher endpoints
    async def create_teacher(self, teacher_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new teacher"""
        return await self._make_request("POST", "/teachers", json=teacher_data)
    
    async def get_teachers(self) -> List[Dict[str, Any]]:
        """Get all teachers"""
        return await self._make_request("GET", "/teachers")
    
    async def get_teacher_by_tg_id(self, tg_id: str) -> Optional[Dict[str, Any]]:
        """Get teacher by Telegram ID"""
        try:
            teachers = await self.get_teachers()
            for teacher in teachers:
                if teacher.get("tg_id") == tg_id:
                    return teacher
            return None
        except APIError:
            return None
    
    # Lesson endpoints
    async def create_lesson(self, lesson_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new lesson"""
        return await self._make_request("POST", "/lessons", json=lesson_data)
    
    async def get_lessons(self, teacher_id: int) -> List[Dict[str, Any]]:
        """Get lessons for teacher"""
        return await self._make_request("GET", f"/lessons?teacher_id={teacher_id}")
    
    async def get_lesson(self, lesson_id: int) -> Dict[str, Any]:
        """Get specific lesson"""
        return await self._make_request("GET", f"/lessons/{lesson_id}")
    
    async def update_lesson(self, lesson_id: int, lesson_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update lesson"""
        return await self._make_request("PATCH", f"/lessons/{lesson_id}", json=lesson_data)
    
    async def delete_lesson(self, lesson_id: int) -> Dict[str, Any]:
        """Delete lesson"""
        return await self._make_request("DELETE", f"/lessons/{lesson_id}")
    
    async def confirm_lesson(self, lesson_id: int) -> Dict[str, Any]:
        """Confirm lesson"""
        return await self._make_request("POST", f"/lessons/{lesson_id}/confirm")
    
    # Invoice endpoints
    async def get_invoices_by_teacher(self, teacher_id: int) -> List[Dict[str, Any]]:
        """Get invoices for teacher"""
        return await self._make_request("GET", f"/invoices/teacher/{teacher_id}")
    
    async def get_invoice_by_lesson(self, lesson_id: int) -> Dict[str, Any]:
        """Get invoice for lesson"""
        return await self._make_request("GET", f"/invoices/lesson/{lesson_id}")
    
    async def update_invoice_status(self, invoice_id: int, status: str) -> Dict[str, Any]:
        """Update invoice status"""
        return await self._make_request("PATCH", f"/invoices/{invoice_id}/status", 
                                      json={"status": status})


# Global API client instance
api_client = TeachersAPIClient()