from core.config import settings
from dataclasses import dataclass


@dataclass
class Order:
    id: str
    link: str
    subject: str = ""
    description: str = ""
    price: str = ""
    time_info: str = ""
    client_name: str = ""

    def get_message(self, accepted: bool = False, reason: str = None):
        message = str(self)
        if accepted:
            message = f"<b>СДЕЛАН ОТКЛИК</b>\n" + message
        elif reason:
            message = f"<b>Не удалось принять заказ</b>\n<i>{reason}</i>\n" + message

        return message

    def __str__(self):
        return f"""
<b>{settings.profi_login}</b>

<b>{self.subject}</b>
<b>{self.price}</b>

{self.description}
<i>{self.time_info}</i>

{self.link}
"""
