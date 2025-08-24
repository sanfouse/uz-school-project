from datetime import datetime, timezone
import enum

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base


class LessonStatus(str, enum.Enum):
    planned = "planned"
    confirmed = "confirmed"
    cancelled = "cancelled"


class LessonType(str, enum.Enum):
    trial = "trial"  # Пробный урок
    regular = "regular"  # Основной урок


class InvoiceStatus(str, enum.Enum):
    unpaid = "unpaid"  # Не оплачен
    paid = "paid"  # Оплачен


class Teacher(Base):
    __tablename__ = "teachers"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=True)
    tg_id: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    bank_account: Mapped[str] = mapped_column(String(64), nullable=False)

    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="teacher", cascade="all,delete"
    )
    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="teacher", cascade="all,delete"
    )


class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id"), nullable=False, index=True
    )
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id"), nullable=False, index=True
    )
    tbank_invoice_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    pdf_url: Mapped[str] = mapped_column(Text, nullable=False)
    incoming_invoice_url: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus), default=InvoiceStatus.unpaid, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    lesson: Mapped["Lesson"] = relationship(back_populates="invoice")
    teacher: Mapped["Teacher"] = relationship(back_populates="invoices")


class Lesson(Base):
    __tablename__ = "lessons"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_name: Mapped[str] = mapped_column(String(255), nullable=False)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id"), nullable=False, index=True
    )
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    status: Mapped[LessonStatus] = mapped_column(
        Enum(LessonStatus), default=LessonStatus.planned, nullable=False
    )
    type: Mapped[LessonType] = mapped_column(
        Enum(LessonType), default=LessonType.regular, nullable=False
    )

    teacher: Mapped[Teacher] = relationship(back_populates="lessons")
    invoice: Mapped[Invoice] = relationship(back_populates="lesson")
