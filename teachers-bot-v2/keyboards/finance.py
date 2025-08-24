from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.navigation import NavigationMixin


class FinanceKeyboards(NavigationMixin):
    """Keyboards for financial management"""
    
    @staticmethod
    def get_finance_dashboard() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text="💳 Мои счета", callback_data="finance:invoices")]
        ]
        
        buttons = NavigationMixin.add_navigation(buttons, show_back=False)
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_invoice_keyboard(invoice_id: int, status: str) -> InlineKeyboardMarkup:
        buttons = []
        
        if status == "unpaid":
            buttons.append([
                InlineKeyboardButton(text="✅ Отметить оплаченным", callback_data=f"invoice:paid:{invoice_id}")
            ])
        
        buttons.extend([
            [InlineKeyboardButton(text="📋 Детали", callback_data=f"invoice:details:{invoice_id}")]
        ])
        
        buttons = NavigationMixin.add_navigation(buttons)
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_earnings_period() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text="📅 За месяц", callback_data="earnings:month")],
            [InlineKeyboardButton(text="📈 За квартал", callback_data="earnings:quarter")],
            [InlineKeyboardButton(text="🗓️ За год", callback_data="earnings:year")],
            [InlineKeyboardButton(text="🔧 Настроить период", callback_data="earnings:custom")]
        ]
        
        buttons = NavigationMixin.add_navigation(buttons)
        return InlineKeyboardMarkup(inline_keyboard=buttons)