from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class RegistrationKeyboards:
    """Keyboards for registration process"""
    
    @staticmethod
    def get_start_registration() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text="🚀 Начать регистрацию", callback_data="register:begin")],
            [InlineKeyboardButton(text="❓ Что это?", callback_data="register:info")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_skip_optional() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text="⏭️ Пропустить", callback_data="register:skip")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="register:back")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_confirmation() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="register:confirm")],
            [InlineKeyboardButton(text="✏️ Изменить", callback_data="register:edit")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="register:cancel")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_edit_field() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text="👤 Имя", callback_data="register:edit:name")],
            [InlineKeyboardButton(text="📞 Телефон", callback_data="register:edit:phone")],
            [InlineKeyboardButton(text="📧 Email", callback_data="register:edit:email")],
            [InlineKeyboardButton(text="🏦 Банк", callback_data="register:edit:bank")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="register:back")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)