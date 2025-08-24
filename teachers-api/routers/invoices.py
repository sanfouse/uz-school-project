from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
import schemas
from services.invoices import (
    get_invoice,
    list_invoices_by_lesson,
    list_invoices_by_teacher,
    update_invoice_status,
    delete_invoice,
)

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/{invoice_id}", response_model=schemas.InvoiceOut)
async def get_invoice_endpoint(
    invoice_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Получает счет по ID"""
    return await get_invoice(db, invoice_id)


@router.get("/lesson/{lesson_id}", response_model=schemas.InvoiceOut)
async def get_invoice_by_lesson_endpoint(
    lesson_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Получает счет для конкретного урока"""
    invoices = await list_invoices_by_lesson(db, lesson_id)
    if not invoices:
        raise HTTPException(404, "Invoice not found for this lesson")
    return invoices[0]  # Возвращаем первый (и единственный) счет


@router.get("/teacher/{teacher_id}", response_model=List[schemas.InvoiceOut])
async def list_invoices_by_teacher_endpoint(
    teacher_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Получает список всех счетов для учителя"""
    return await list_invoices_by_teacher(db, teacher_id)


@router.patch("/{invoice_id}/status", response_model=schemas.InvoiceOut)
async def update_invoice_status_endpoint(
    invoice_id: int,
    status_update: schemas.InvoiceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Обновляет статус счета"""
    return await update_invoice_status(db, invoice_id, status_update.status)


@router.delete("/{invoice_id}")
async def delete_invoice_endpoint(
    invoice_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Удаляет счет"""
    return await delete_invoice(db, invoice_id)
