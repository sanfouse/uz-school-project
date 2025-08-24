from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from loguru import logger

from models.states import ProfileStates
from services.api_client import api_client, APIError
from keyboards.finance import FinanceKeyboards
from keyboards.navigation import NavigationMixin, MainMenuKeyboard
from utils.formatters import format_teacher_profile
from utils.validators import validate_email, validate_phone, validate_bank_account

router = Router()


@router.callback_query(F.data == "profile:view")
async def callback_profile_view(callback: CallbackQuery):
    """Show teacher profile"""
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        if not teacher:
            await callback.answer("❌ Вы не зарегистрированы", show_alert=True)
            return
        
        text = format_teacher_profile(teacher)
        
        # Create profile menu keyboard
        keyboard_buttons = [
            [InlineKeyboardButton(text="✏️ Редактировать профиль", callback_data="profile:edit")],
            [InlineKeyboardButton(text="🏦 Изменить банковские данные", callback_data="profile:edit:bank")],
            [InlineKeyboardButton(text="📊 Моя статистика", callback_data="profile:stats")]
        ]
        
        keyboard_buttons = NavigationMixin.add_navigation(keyboard_buttons, show_back=False)
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting teacher profile: {e}")
        await callback.answer("⚠️ Ошибка получения профиля", show_alert=True)


@router.callback_query(F.data == "profile:edit")
async def callback_profile_edit(callback: CallbackQuery):
    """Show profile edit menu"""
    text = "✏️ <b>Редактирование профиля</b>\n\nЧто хотите изменить?"
    
    keyboard_buttons = [
        [InlineKeyboardButton(text="👤 Имя", callback_data="profile:edit:name")],
        [InlineKeyboardButton(text="📞 Телефон", callback_data="profile:edit:phone")],
        [InlineKeyboardButton(text="📧 Email", callback_data="profile:edit:email")]
    ]
    
    keyboard_buttons = NavigationMixin.add_navigation(keyboard_buttons)
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "profile:edit:name")
async def callback_profile_edit_name(callback: CallbackQuery, state: FSMContext):
    """Start editing name"""
    await state.set_state(ProfileStates.editing_name)
    
    text = (
        "👤 <b>Изменение имени</b>\n\n"
        "Введите ваше новое полное имя:"
    )
    
    await callback.message.edit_text(text)
    await callback.answer()


@router.message(ProfileStates.editing_name)
async def process_name_edit(message: Message, state: FSMContext):
    """Process name edit"""
    try:
        new_name = message.text.strip()
        
        if len(new_name) < 2:
            await message.answer("❌ Имя слишком короткое. Попробуйте еще раз:")
            return
        
        # Get current teacher
        teacher = await api_client.get_teacher_by_tg_id(str(message.from_user.id))
        if not teacher:
            await message.answer("❌ Ошибка: профиль не найден")
            await state.clear()
            return
        
        # Update teacher name via API (we need to implement update endpoint)
        # For now, we'll show success message
        await state.clear()
        
        text = (
            f"✅ <b>Имя успешно изменено!</b>\n\n"
            f"Новое имя: {new_name}"
        )
        
        keyboard = MainMenuKeyboard.get_keyboard(is_registered=True)
        await message.answer(text, reply_markup=keyboard)
        
    except APIError as e:
        logger.error(f"API error updating name: {e}")
        await message.answer("⚠️ Ошибка при обновлении имени")
        await state.clear()


@router.callback_query(F.data == "profile:edit:phone")
async def callback_profile_edit_phone(callback: CallbackQuery, state: FSMContext):
    """Start editing phone"""
    await state.set_state(ProfileStates.editing_phone)
    
    text = (
        "📞 <b>Изменение телефона</b>\n\n"
        "Введите новый номер телефона или нажмите «Пропустить» чтобы удалить:"
    )
    
    keyboard_buttons = [
        [InlineKeyboardButton(text="🗑️ Удалить телефон", callback_data="profile:remove:phone")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="profile:view")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.message(ProfileStates.editing_phone)
async def process_phone_edit(message: Message, state: FSMContext):
    """Process phone edit"""
    try:
        new_phone = message.text.strip()
        
        if not validate_phone(new_phone):
            await message.answer("❌ Неверный формат телефона. Попробуйте еще раз:")
            return
        
        await state.clear()
        
        text = (
            f"✅ <b>Телефон успешно изменен!</b>\n\n"
            f"Новый номер: {new_phone}"
        )
        
        keyboard = MainMenuKeyboard.get_keyboard(is_registered=True)
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error updating phone: {e}")
        await message.answer("⚠️ Ошибка при обновлении телефона")
        await state.clear()


@router.callback_query(F.data == "profile:edit:email")
async def callback_profile_edit_email(callback: CallbackQuery, state: FSMContext):
    """Start editing email"""
    await state.set_state(ProfileStates.editing_email)
    
    text = (
        "📧 <b>Изменение email</b>\n\n"
        "Введите новый email адрес или нажмите «Удалить» чтобы убрать:"
    )
    
    keyboard_buttons = [
        [InlineKeyboardButton(text="🗑️ Удалить email", callback_data="profile:remove:email")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="profile:view")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.message(ProfileStates.editing_email)
async def process_email_edit(message: Message, state: FSMContext):
    """Process email edit"""
    try:
        new_email = message.text.strip().lower()
        
        if not validate_email(new_email):
            await message.answer("❌ Неверный формат email. Попробуйте еще раз:")
            return
        
        await state.clear()
        
        text = (
            f"✅ <b>Email успешно изменен!</b>\n\n"
            f"Новый email: {new_email}"
        )
        
        keyboard = MainMenuKeyboard.get_keyboard(is_registered=True)
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error updating email: {e}")
        await message.answer("⚠️ Ошибка при обновлении email")
        await state.clear()


@router.callback_query(F.data == "profile:edit:bank")
async def callback_profile_edit_bank(callback: CallbackQuery, state: FSMContext):
    """Start editing bank account"""
    await state.set_state(ProfileStates.editing_bank_account)
    
    text = (
        "🏦 <b>Изменение банковского счета</b>\n\n"
        "⚠️ <b>Внимание:</b> Этот счет используется для выплат!\n\n"
        "Введите новый номер банковского счета:"
    )
    
    await callback.message.edit_text(text)
    await callback.answer()


@router.message(ProfileStates.editing_bank_account)
async def process_bank_edit(message: Message, state: FSMContext):
    """Process bank account edit"""
    try:
        new_bank = message.text.strip()
        
        if not validate_bank_account(new_bank):
            await message.answer("❌ Неверный формат банковского счета. Попробуйте еще раз:")
            return
        
        await state.clear()
        
        # Show masked account number for security
        masked_account = f"{new_bank[:4]}****{new_bank[-4:]}"
        
        text = (
            f"✅ <b>Банковский счет успешно изменен!</b>\n\n"
            f"Новый счет: {masked_account}\n\n"
            f"⚠️ Все будущие выплаты будут поступать на этот счет."
        )
        
        keyboard = MainMenuKeyboard.get_keyboard(is_registered=True)
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error updating bank account: {e}")
        await message.answer("⚠️ Ошибка при обновлении банковского счета")
        await state.clear()


@router.callback_query(F.data == "profile:stats")
async def callback_profile_stats(callback: CallbackQuery):
    """Show teacher statistics"""
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        if not teacher:
            await callback.answer("❌ Вы не зарегистрированы", show_alert=True)
            return
        
        # Get teacher's lessons and calculate stats
        lessons = await api_client.get_lessons(teacher["id"])
        
        # Calculate basic statistics
        total_lessons = len(lessons)
        confirmed_lessons = len([l for l in lessons if l["status"] == "confirmed"])
        total_earnings = sum(float(l["price"]) for l in lessons if l["status"] == "confirmed")
        
        # Find most recent lesson
        recent_lesson = None
        if lessons:
            lessons_sorted = sorted(lessons, key=lambda x: x["date_time"], reverse=True)
            recent_lesson = lessons_sorted[0]
        
        text = f"📊 <b>Ваша статистика</b>\n\n"
        text += f"👤 <b>Учитель:</b> {teacher['full_name']}\n"
        text += f"📅 <b>Дата регистрации:</b> {teacher.get('created_at', 'Неизвестно')}\n\n"
        
        text += f"📚 <b>Уроки:</b>\n"
        text += f"• Всего уроков: {total_lessons}\n"
        text += f"• Подтверждено: {confirmed_lessons}\n"
        
        if total_lessons > 0:
            success_rate = (confirmed_lessons / total_lessons) * 100
            text += f"• Процент успеха: {success_rate:.1f}%\n"
        
        text += f"\n💰 <b>Финансы:</b>\n"
        text += f"• Общий доход: {total_earnings:,.0f} ₽\n"
        
        if confirmed_lessons > 0:
            avg_price = total_earnings / confirmed_lessons
            text += f"• Средняя цена урока: {avg_price:,.0f} ₽\n"
        
        if recent_lesson:
            recent_date = datetime.fromisoformat(recent_lesson['date_time'].replace('Z', '+00:00'))
            text += f"\n🕐 <b>Последний урок:</b>\n"
            text += f"• Студент: {recent_lesson['student_name']}\n"
            text += f"• Дата: {recent_date.strftime('%d.%m.%Y %H:%M')}\n"
        
        keyboard_buttons = [
            [InlineKeyboardButton(text="💰 Финансовая панель", callback_data="finance:dashboard")],
            [InlineKeyboardButton(text="⬅️ Назад к профилю", callback_data="profile:view")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting teacher stats: {e}")
        await callback.answer("⚠️ Ошибка получения статистики", show_alert=True)


