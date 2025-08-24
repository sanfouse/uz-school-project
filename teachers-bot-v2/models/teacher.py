from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from enum import Enum


class LessonStatus(str, Enum):
    planned = "planned"
    confirmed = "confirmed"
    cancelled = "cancelled"


class LessonType(str, Enum):
    trial = "trial"
    regular = "regular"


class InvoiceStatus(str, Enum):
    unpaid = "unpaid"
    paid = "paid"


class Teacher(BaseModel):
    id: int
    full_name: str
    phone: Optional[str] = None
    tg_id: str
    email: Optional[EmailStr] = None
    bank_account: str


class Lesson(BaseModel):
    id: int
    student_name: str
    teacher_id: int
    price: float
    date_time: datetime
    status: LessonStatus
    type: LessonType


class Invoice(BaseModel):
    id: int
    lesson_id: int
    teacher_id: int
    tbank_invoice_id: str
    pdf_url: str
    incoming_invoice_url: str
    status: InvoiceStatus
    created_at: datetime


class CreateTeacherRequest(BaseModel):
    full_name: str
    phone: Optional[str] = None
    tg_id: str
    email: Optional[EmailStr] = None
    bank_account: str


class CreateLessonRequest(BaseModel):
    student_name: str
    teacher_id: int
    price: float
    date_time: datetime
    type: LessonType = LessonType.regular


class UpdateLessonRequest(BaseModel):
    student_name: Optional[str] = None
    price: Optional[float] = None
    date_time: Optional[datetime] = None
    type: Optional[LessonType] = None
    status: Optional[LessonStatus] = None