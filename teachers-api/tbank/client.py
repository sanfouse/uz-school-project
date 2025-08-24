import httpx
import uuid

from core.config import settings


class TBankClient:
    def __init__(self, token: str | None = None):
        self.base_url = "https://business.tbank.ru/openapi/sandbox/api/v1/invoice/send"
        self.token = token or settings.TINKOFF_TOKEN
        self._client = httpx.Client(timeout=20.0)

    def send_invoice(self, payload: dict) -> dict:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Request-Id": str(uuid.uuid4()),
        }
        resp = self._client.post(self.base_url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def parse_invoice_response(self, response: dict) -> dict:
        """Парсит ответ от Т-Банка и возвращает структурированные данные"""
        return {
            "pdf_url": response.get("pdfUrl", ""),
            "tbank_invoice_id": response.get("invoiceId", ""),
            "incoming_invoice_url": response.get("incomingInvoiceUrl", ""),
        }
