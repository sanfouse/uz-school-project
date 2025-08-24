from typing import Optional

from pydantic import BaseModel, EmailStr


class TeacherCreate(BaseModel):
    full_name: str
    phone: Optional[str] = None
    tg_id: str
    email: Optional[EmailStr] = None
    bank_account: str


class TeacherUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    tg_id: Optional[str] = None
    email: Optional[EmailStr] = None
    bank_account: Optional[str] = None


class TeacherOut(TeacherCreate):
    id: int

    class Config:
        from_attributes = True
