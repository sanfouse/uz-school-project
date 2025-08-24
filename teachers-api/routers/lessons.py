from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from schemas.lessons import LessonCreate, LessonOut, LessonUpdate
from services.lessons import (
    confirm_lesson,
    create_lesson,
    delete_lesson,
    get_lesson,
    list_lessons,
    update_lesson,
)

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.post("")
async def create_lesson_endpoint(
    payload: LessonCreate, db: Annotated[AsyncSession, Depends(get_db)]
) -> LessonOut:
    return await create_lesson(db, payload)


@router.get("")
async def list_lessons_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)], teacher_id: int
) -> list[LessonOut]:
    return await list_lessons(db, teacher_id)


@router.get("/{lesson_id}")
async def get_lesson_endpoint(
    lesson_id: int, db: Annotated[AsyncSession, Depends(get_db)]
) -> LessonOut:
    return await get_lesson(db, lesson_id)


@router.patch("/{lesson_id}")
async def update_lesson_endpoint(
    lesson_id: int,
    payload: LessonUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LessonOut:
    return await update_lesson(db, lesson_id, payload)


@router.delete("/{lesson_id}")
async def delete_lesson_endpoint(
    lesson_id: int, db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    return await delete_lesson(db, lesson_id)


@router.post("/{lesson_id}/confirm")
async def confirm_lesson_endpoint(
    lesson_id: int, db: Annotated[AsyncSession, Depends(get_db)]
) -> LessonOut:
    return await confirm_lesson(db, lesson_id)
