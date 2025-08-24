from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from loguru import logger

from core.bot import bot
from services.api_client import api_client, APIError
from keyboards.navigation import MainMenuKeyboard, QuickActionsKeyboard
from utils.formatters import format_welcome_message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(message.from_user.id))
        
        if teacher:
            # Registered user
            welcome_text = format_welcome_message(teacher["full_name"])
            keyboard = MainMenuKeyboard.get_keyboard(is_registered=True)
            
            await message.answer(welcome_text, reply_markup=keyboard)
            
            # Show quick actions
            quick_actions_text = "🚀 <b>Быстрые действия:</b>"
            quick_keyboard = QuickActionsKeyboard.get_keyboard()
            await message.answer(quick_actions_text, reply_markup=quick_keyboard)
            
        else:
            # New user - needs registration
            welcome_text = (
                "👋 <b>Добро пожаловать!</b>\n\n"
                "Я помогу вам управлять уроками, студентами и финансами.\n\n"
                "Для начала работы необходимо зарегистрироваться."
            )
            keyboard = MainMenuKeyboard.get_keyboard(is_registered=False)
            await message.answer(welcome_text, reply_markup=keyboard)
            
    except APIError as e:
        logger.error(f"API error in start command: {e}")
        await message.answer(
            "⚠️ Произошла ошибка при подключении к серверу. Попробуйте позже."
        )
    except Exception as e:
        logger.error(f"Unexpected error in start command: {e}")
        await message.answer(
            "❌ Произошла неожиданная ошибка. Обратитесь к администратору."
        )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Handle /menu command - show main menu"""
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(message.from_user.id))
        
        if teacher:
            text = "🏠 <b>Главное меню</b>\n\nВыберите нужный раздел:"
            keyboard = MainMenuKeyboard.get_keyboard(is_registered=True)
        else:
            text = "📝 <b>Регистрация</b>\n\nДля использования бота необходимо зарегистрироваться:"
            keyboard = MainMenuKeyboard.get_keyboard(is_registered=False)
        
        await message.answer(text, reply_markup=keyboard)
        
    except APIError as e:
        logger.error(f"API error in menu command: {e}")
        await message.answer("⚠️ Ошибка подключения к серверу.")


@router.callback_query(F.data == "nav:home")
async def callback_nav_home(callback: CallbackQuery):
    """Navigate to home menu"""
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        
        if teacher:
            text = "🏠 <b>Главное меню</b>\n\nВыберите нужный раздел:"
            keyboard = MainMenuKeyboard.get_keyboard(is_registered=True)
        else:
            text = "📝 <b>Регистрация</b>\n\nДля использования бота необходимо зарегистрироваться:"
            keyboard = MainMenuKeyboard.get_keyboard(is_registered=False)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error in nav home: {e}")
        await callback.answer("⚠️ Ошибка подключения к серверу.", show_alert=True)


@router.callback_query(F.data == "nav:back")
async def callback_nav_back(callback: CallbackQuery):
    """Navigate back - return to appropriate parent menu"""
    # For now, redirect to main menu since we don't have navigation history
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        
        if teacher:
            text = "🏠 <b>Главное меню</b>\n\nВыберите нужный раздел:"
            keyboard = MainMenuKeyboard.get_keyboard(is_registered=True)
        else:
            text = "📝 <b>Регистрация</b>\n\nДля использования бота необходимо зарегистрироваться:"
            keyboard = MainMenuKeyboard.get_keyboard(is_registered=False)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error in nav back: {e}")
        await callback.answer("⚠️ Ошибка подключения к серверу.", show_alert=True)


@router.callback_query(F.data == "help:main")
async def callback_help_main(callback: CallbackQuery):
    """Show main help"""
    help_text = """
🆘 <b>Справка по боту</b>

<b>Основные функции:</b>
• 📚 <b>Уроки</b> - управление расписанием и уроками
• 💰 <b>Финансы</b> - отслеживание доходов и счетов
• 👤 <b>Профиль</b> - редактирование личных данных

<b>Команды:</b>
/start - главное меню
/menu - показать меню
/help - эта справка

<b>Поддержка:</b>
При возникновении проблем обратитесь к администратору.
    """
    
    await callback.message.edit_text(help_text, reply_markup=MainMenuKeyboard.get_keyboard(True))
    await callback.answer()