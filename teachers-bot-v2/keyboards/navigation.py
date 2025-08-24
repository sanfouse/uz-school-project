from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class NavigationMixin:
    """Base class for navigation utilities"""
    
    @staticmethod
    def get_back_home_buttons() -> List[List[InlineKeyboardButton]]:
        return [[
            InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:back"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="nav:home")
        ]]
    
    @staticmethod
    def add_navigation(buttons: List[List[InlineKeyboardButton]], 
                     show_back: bool = True, 
                     show_home: bool = True) -> List[List[InlineKeyboardButton]]:
        if show_back or show_home:
            nav_buttons = []
            if show_back:
                nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:back"))
            if show_home:
                nav_buttons.append(InlineKeyboardButton(text="🏠 Главное меню", callback_data="nav:home"))
            buttons.append(nav_buttons)
        return buttons


class MainMenuKeyboard:
    """Main menu with primary sections"""
    
    @staticmethod
    def get_keyboard(is_registered: bool = True) -> InlineKeyboardMarkup:
        if not is_registered:
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📝 Регистрация", callback_data="register:start")],
                [InlineKeyboardButton(text="❓ Помощь", callback_data="help:main")]
            ])
        
        buttons = [
            [InlineKeyboardButton(text="📚 Мои уроки", callback_data="lessons:menu")],
            [InlineKeyboardButton(text="💰 Финансы", callback_data="finance:dashboard")],
            [InlineKeyboardButton(text="👤 Профиль", callback_data="profile:view")],
            [InlineKeyboardButton(text="❓ Помощь", callback_data="help:main")]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)


class QuickActionsKeyboard:
    """Quick action buttons for common tasks"""
    
    @staticmethod
    def get_keyboard() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text="➕ Быстро создать урок", callback_data="lesson:quick_create")],
            [InlineKeyboardButton(text="📊 Сегодняшние уроки", callback_data="lessons:today")],
            [InlineKeyboardButton(text="💳 Мои счета", callback_data="finance:invoices")]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)