from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas.teachers import TeacherCreate, TeacherUpdate
from core.notifications import notification_service


async def create_teacher(db: AsyncSession, payload: TeacherCreate) -> models.Teacher:
    """Создает нового учителя"""
    # Проверяем, что учитель с таким tg_id не существует
    exists = await db.execute(
        select(models.Teacher).filter(models.Teacher.tg_id == payload.tg_id)
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Teacher with tg_id exists")

    teacher = models.Teacher(**payload.model_dump())
    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    
    # Send notification
    teacher_data = {
        "id": teacher.id,
        "full_name": teacher.full_name,
        "email": teacher.email,
        "tg_id": teacher.tg_id
    }
    await notification_service.teacher_registered(teacher_data)
    
    return teacher


async def get_teacher(db: AsyncSession, teacher_id: int) -> models.Teacher:
    """Получает учителя по ID"""
    teacher = await db.get(models.Teacher, teacher_id)
    if not teacher:
        raise HTTPException(404, "Teacher not found")
    return teacher


async def list_teachers(db: AsyncSession) -> List[models.Teacher]:
    """Получает список всех учителей"""
    result = await db.execute(select(models.Teacher))
    return result.scalars().all()


async def update_teacher(
    db: AsyncSession, teacher_id: int, payload: TeacherUpdate
) -> models.Teacher:
    """Обновляет учителя"""
    teacher = await db.get(models.Teacher, teacher_id)
    if not teacher:
        raise HTTPException(404, "Teacher not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(teacher, k, v)

    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    return teacher


async def delete_teacher(db: AsyncSession, teacher_id: int) -> dict:
    """Удаляет учителя"""
    teacher = await db.get(models.Teacher, teacher_id)
    if not teacher:
        raise HTTPException(404, "Teacher not found")

    await db.delete(teacher)
    await db.commit()
    return {"ok": True}
