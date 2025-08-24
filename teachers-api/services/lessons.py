from datetime import timedelta
from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Lesson, LessonStatus, Teacher, Invoice
from schemas.lessons import LessonCreate, LessonUpdate
from tbank.client import TBankClient
from core.notifications import notification_service


async def create_lesson(db: AsyncSession, payload: LessonCreate) -> Lesson:
    """Создает новый урок"""
    # Проверяем существование учителя
    teacher = await db.execute(select(Teacher).where(Teacher.id == payload.teacher_id))
    teacher = teacher.scalar_one_or_none()
    if not teacher:
        raise HTTPException(404, "Teacher not found")

    lesson = Lesson(**payload.model_dump())
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    # Send notification
    lesson_data = {
        "id": lesson.id,
        "student_name": lesson.student_name,
        "date_time": lesson.date_time.isoformat(),
        "price": str(lesson.price),
        "type": lesson.type
    }
    await notification_service.lesson_created(lesson_data, lesson.teacher_id)

    return lesson


async def get_lesson(db: AsyncSession, lesson_id: int) -> Lesson:
    """Получает урок по ID"""
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    return lesson


async def list_lessons(db: AsyncSession, teacher_id: int) -> List[Lesson]:
    """Получает список уроков для учителя"""
    result = await db.execute(select(Lesson).filter(Lesson.teacher_id == teacher_id))
    return result.scalars().all()


async def update_lesson(
    db: AsyncSession, lesson_id: int, payload: LessonUpdate
) -> Lesson:
    """Обновляет урок"""
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")

    data = payload.model_dump(exclude_unset=True)
    date_time_changed = "date_time" in data

    # Применяем изменения
    for k, v in data.items():
        setattr(lesson, k, v)

    # Если изменилось время, сбрасываем статус подтверждения
    if date_time_changed:
        lesson.status = LessonStatus.planned

    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    # Send notification
    lesson_data = {
        "id": lesson.id,
        "student_name": lesson.student_name,
        "date_time": lesson.date_time.isoformat(),
        "price": str(lesson.price)
    }
    await notification_service.lesson_updated(lesson_data, lesson.teacher_id, data)

    return lesson


async def delete_lesson(db: AsyncSession, lesson_id: int) -> dict:
    """Удаляет урок"""
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")

    # Store lesson data for notification before deletion
    lesson_data = {
        "id": lesson.id,
        "student_name": lesson.student_name,
        "date_time": lesson.date_time.isoformat(),
        "reason": "Lesson deleted"
    }
    teacher_id = lesson.teacher_id

    await db.delete(lesson)
    await db.commit()
    
    # Send notification
    await notification_service.lesson_cancelled(lesson_data, teacher_id)
    
    return {"ok": True}


async def confirm_lesson(db: AsyncSession, lesson_id: int) -> Lesson:
    """Подтверждает урок и создает счет"""
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")

    if lesson.status != LessonStatus.planned:
        raise HTTPException(409, "Lesson not in confirmable state")

    # Проверяем, не существует ли уже счет для этого урока
    from sqlalchemy import select
    existing_invoice = await db.execute(
        select(Invoice).where(Invoice.lesson_id == lesson_id)
    )
    if existing_invoice.scalars().first():
        raise HTTPException(409, "Invoice already exists for this lesson")

    teacher = await db.get(Teacher, lesson.teacher_id)

    # Создаем счет через Т-Банк
    invoice_payload = {
        "invoiceNumber": str(lesson.id),
        "dueDate": (lesson.date_time.date() + timedelta(days=10)).isoformat(),
        "invoiceDate": lesson.date_time.date().isoformat(),
        "accountNumber": teacher.bank_account,
        "payer": {
            "name": lesson.student_name,
            "inn": "524927736002",
            "kpp": "000000000",
        },
        "items": [
            {
                "name": f"тест",
                "price": float(lesson.price),
                "unit": "шт",
                "vat": "None",  # Должен быть строкой согласно API
                "amount": 1,
            }
        ],
        "contacts": (
            [{"email": teacher.email}]
            if teacher.email
            else [{"email": "test@example.com"}]
        ),
        "contactPhone": "+79201337199",
        "comment": f"тест",
        "customPaymentPurpose": f"тест",
    }

    client = TBankClient()
    try:
        resp = client.send_invoice(invoice_payload)
        invoice_data = client.parse_invoice_response(resp)

        # Проверяем, что получили все необходимые данные
        if not invoice_data["pdf_url"] or not invoice_data["tbank_invoice_id"]:
            raise HTTPException(502, "T-Bank не вернул необходимые данные")

    except Exception as e:
        raise HTTPException(502, f"T-Bank error: {e}")

    # Создаем запись о счете
    invoice = Invoice(
        lesson_id=lesson.id,
        teacher_id=teacher.id,
        tbank_invoice_id=invoice_data["tbank_invoice_id"],
        pdf_url=invoice_data["pdf_url"],
        incoming_invoice_url=invoice_data["incoming_invoice_url"],
    )
    db.add(invoice)

    # Обновляем статус урока
    lesson.status = LessonStatus.confirmed
    db.add(lesson)

    await db.commit()
    await db.refresh(lesson)

    # Send notification
    lesson_data = {
        "id": lesson.id,
        "student_name": lesson.student_name,
        "date_time": lesson.date_time.isoformat(),
        "price": str(lesson.price)
    }
    await notification_service.lesson_confirmed(lesson_data, lesson.teacher_id)

    return lesson
