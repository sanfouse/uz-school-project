from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

import models
from core.notifications import notification_service


async def get_invoice(db: AsyncSession, invoice_id: int) -> models.Invoice:
    """Получает счет по ID"""
    invoice = await db.get(models.Invoice, invoice_id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    return invoice


async def list_invoices_by_lesson(
    db: AsyncSession, lesson_id: int
) -> List[models.Invoice]:
    """Получает список счетов для урока"""
    result = await db.execute(
        select(models.Invoice).filter(models.Invoice.lesson_id == lesson_id)
    )
    return result.scalars().all()


async def list_invoices_by_teacher(
    db: AsyncSession, teacher_id: int
) -> List[models.Invoice]:
    """Получает список счетов для учителя"""
    result = await db.execute(
        select(models.Invoice).filter(models.Invoice.teacher_id == teacher_id)
    )
    return result.scalars().all()


async def update_invoice_status(
    db: AsyncSession, invoice_id: int, status: models.InvoiceStatus
) -> models.Invoice:
    """Обновляет статус счета"""
    invoice = await db.get(models.Invoice, invoice_id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")

    old_status = invoice.status
    invoice.status = status
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    
    # Send notification if invoice was marked as paid
    if old_status != models.InvoiceStatus.paid and status == models.InvoiceStatus.paid:
        invoice_data = {
            "id": invoice.id,
            "lesson_id": invoice.lesson_id,
            "tbank_invoice_id": invoice.tbank_invoice_id
        }
        await notification_service.invoice_paid(invoice_data, invoice.teacher_id)

    return invoice


async def delete_invoice(db: AsyncSession, invoice_id: int) -> dict:
    """Удаляет счет"""
    invoice = await db.get(models.Invoice, invoice_id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")

    await db.delete(invoice)
    await db.commit()
    return {"ok": True}
