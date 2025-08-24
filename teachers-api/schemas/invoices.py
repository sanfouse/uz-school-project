from pydantic import BaseModel
from datetime import datetime
import models


class InvoiceBase(BaseModel):
    lesson_id: int
    teacher_id: int
    tbank_invoice_id: str
    pdf_url: str
    incoming_invoice_url: str
    status: models.InvoiceStatus = models.InvoiceStatus.unpaid


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    status: models.InvoiceStatus


class InvoiceOut(InvoiceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
