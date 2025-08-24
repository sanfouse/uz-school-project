from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

import models


class LessonBase(BaseModel):
    student_name: str
    teacher_id: int
    type: models.LessonType = models.LessonType.regular
    price: float = Field(gt=0)
    date_time: datetime


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    student_name: Optional[str] = None
    type: Optional[models.LessonType] = None
    price: Optional[float] = Field(default=None, gt=0)
    date_time: Optional[datetime] = None
    status: Optional[models.LessonStatus] = None


class LessonOut(BaseModel):
    id: int
    student_name: str
    teacher_id: int
    type: models.LessonType
    price: float
    date_time: datetime
    status: models.LessonStatus
    invoice_url: Optional[str] = None

    class Config:
        from_attributes = True
