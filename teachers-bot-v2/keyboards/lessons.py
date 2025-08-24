from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.navigation import NavigationMixin


class LessonKeyboards(NavigationMixin):
    """Keyboards for lesson management"""
    
    @staticmethod
    def get_lessons_menu() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text="📋 Все уроки", callback_data="lessons:list")],
            [InlineKeyboardButton(text="⏰ Сегодня", callback_data="lessons:today")],
            [InlineKeyboardButton(text="📅 На неделю", callback_data="lessons:week")],
            [InlineKeyboardButton(text="➕ Создать урок", callback_data="lesson:create")]
        ]
        
        buttons = NavigationMixin.add_navigation(buttons, show_back=False)
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_lesson_detail_keyboard(lesson_id: int, status: str = "planned") -> InlineKeyboardMarkup:
        buttons = []
        
        # Status-specific actions
        if status == "planned":
            buttons.extend([
                [
                    InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"lesson:confirm:{lesson_id}"),
                    InlineKeyboardButton(text="❌ Отменить", callback_data=f"lesson:cancel:{lesson_id}")
                ]
            ])
        
        # Common actions
        buttons.extend([
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"lesson:edit:{lesson_id}")],
            [InlineKeyboardButton(text="👤 Студент", callback_data=f"lesson:student:{lesson_id}")],
            [InlineKeyboardButton(text="💰 Счет", callback_data=f"lesson:invoice:{lesson_id}")],
            [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"lesson:delete:{lesson_id}")]
        ])
        
        buttons = NavigationMixin.add_navigation(buttons)
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_lesson_edit_keyboard(lesson_id: int) -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text="👤 Имя студента", callback_data=f"lesson:edit:name:{lesson_id}")],
            [InlineKeyboardButton(text="💰 Цена", callback_data=f"lesson:edit:price:{lesson_id}")],
            [InlineKeyboardButton(text="📅 Дата", callback_data=f"lesson:edit:date:{lesson_id}")],
            [InlineKeyboardButton(text="⏰ Время", callback_data=f"lesson:edit:time:{lesson_id}")],
            [InlineKeyboardButton(text="📝 Тип", callback_data=f"lesson:edit:type:{lesson_id}")]
        ]
        
        buttons = NavigationMixin.add_navigation(buttons)
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_lesson_type_keyboard() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text="🎯 Пробный урок", callback_data="lesson:type:trial")],
            [InlineKeyboardButton(text="📚 Основной урок", callback_data="lesson:type:regular")]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_lesson_confirmation_keyboard(lesson_id: int) -> InlineKeyboardMarkup:
        """Keyboard for lesson confirmation notifications"""
        buttons = [
            [
                InlineKeyboardButton(text="✅ Урок состоялся", callback_data=f"confirm:lesson:{lesson_id}"),
                InlineKeyboardButton(text="❌ Урок не состоялся", callback_data=f"cancel:lesson:{lesson_id}")
            ],
            [InlineKeyboardButton(text="📝 Детали урока", callback_data=f"lesson:details:{lesson_id}")]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)