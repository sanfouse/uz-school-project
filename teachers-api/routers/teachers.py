from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.teachers import TeacherOut, TeacherCreate

from core.db import get_db
from services.teachers import create_teacher, list_teachers

router = APIRouter(prefix="/teachers", tags=["teachers"])


@router.post("")
async def create_teacher_endpoint(
    payload: TeacherCreate, db: Annotated[AsyncSession, Depends(get_db)]
) -> TeacherOut:
    return await create_teacher(db, payload)


@router.get("")
async def list_teachers_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TeacherOut]:
    return await list_teachers(db)
