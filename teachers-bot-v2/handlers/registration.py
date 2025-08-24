from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger
import re

from models.states import RegistrationStates
from services.api_client import api_client, APIError
from keyboards.registration import RegistrationKeyboards
from keyboards.navigation import MainMenuKeyboard
from utils.formatters import format_registration_confirmation
from utils.validators import validate_email, validate_phone, validate_bank_account

router = Router()


@router.callback_query(F.data == "register:start")
async def callback_register_start(callback: CallbackQuery):
    """Start registration process"""
    text = (
        "📝 <b>Регистрация учителя</b>\n\n"
        "Для работы с ботом необходимо пройти быструю регистрацию.\n\n"
        "Мы соберем основную информацию:\n"
        "• Ваше имя\n"
        "• Телефон\n"
        "• Email\n"
        "• Банковские реквизиты для выплат\n\n"
        "Готовы начать?"
    )
    
    keyboard = RegistrationKeyboards.get_start_registration()
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "register:info")
async def callback_register_info(callback: CallbackQuery):
    """Show registration info"""
    text = (
        "ℹ️ <b>О регистрации</b>\n\n"
        "<b>Зачем нужна регистрация?</b>\n"
        "• Персонализация интерфейса\n"
        "• Управление вашими уроками\n"
        "• Отслеживание доходов\n"
        "• Автоматическое создание счетов\n\n"
        "<b>Безопасность данных:</b>\n"
        "• Все данные надежно защищены\n"
        "• Используются только для работы системы\n"
        "• Банковские данные не сохраняются в открытом виде\n\n"
        "Готовы продолжить?"
    )
    
    keyboard = RegistrationKeyboards.get_start_registration()
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "register:begin")
async def callback_register_begin(callback: CallbackQuery, state: FSMContext):
    """Begin registration process"""
    await state.set_state(RegistrationStates.waiting_for_name)
    
    text = (
        "👤 <b>Шаг 1 из 4</b>\n\n"
        "Введите ваше полное имя:\n\n"
        "<i>Например: Иванов Иван Иванович</i>"
    )
    
    await callback.message.edit_text(text)
    await callback.answer()


@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Process teacher name input"""
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer("❌ Имя слишком короткое. Попробуйте еще раз:")
        return
    
    if len(name) > 255:
        await message.answer("❌ Имя слишком длинное. Попробуйте еще раз:")
        return
    
    await state.update_data(full_name=name)
    await state.set_state(RegistrationStates.waiting_for_phone)
    
    text = (
        "📞 <b>Шаг 2 из 4</b>\n\n"
        "Введите ваш номер телефона:\n\n"
        "<i>Например: +7 999 123-45-67</i>"
    )
    
    await message.answer(text)


@router.message(RegistrationStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Process phone number input"""
    phone = message.text.strip()
    
    if not validate_phone(phone):
        await message.answer("❌ Неверный формат телефона. Попробуйте еще раз:")
        return
    
    await state.update_data(phone=phone)
    await _next_step_email(message, state)




async def _next_step_email(message: Message, state: FSMContext):
    """Move to email step"""
    await state.set_state(RegistrationStates.waiting_for_email)
    
    text = (
        "📧 <b>Шаг 3 из 4</b>\n\n"
        "Введите ваш email:\n\n"
        "<i>Например: teacher@example.com</i>"
    )
    
    await message.answer(text)


@router.message(RegistrationStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    """Process email input"""
    email = message.text.strip().lower()
    
    if not validate_email(email):
        await message.answer("❌ Неверный формат email. Попробуйте еще раз:")
        return
    
    await state.update_data(email=email)
    await _next_step_bank(message, state)




async def _next_step_bank(message: Message, state: FSMContext):
    """Move to bank account step"""
    await state.set_state(RegistrationStates.waiting_for_bank_account)
    
    text = (
        "🏦 <b>Шаг 4 из 4</b>\n\n"
        "Введите номер банковского счета для выплат:\n\n"
        "<i>Например: 40817810123456789012</i>\n\n"
        "⚠️ <b>Внимание:</b> Этот счет будет использоваться для переводов!"
    )
    
    await message.answer(text)


@router.message(RegistrationStates.waiting_for_bank_account)
async def process_bank_account(message: Message, state: FSMContext):
    """Process bank account input"""
    bank_account = message.text.strip()
    
    if not validate_bank_account(bank_account):
        await message.answer("❌ Неверный формат банковского счета. Попробуйте еще раз:")
        return
    
    await state.update_data(bank_account=bank_account)
    await state.set_state(RegistrationStates.confirmation)
    
    # Show confirmation
    data = await state.get_data()
    text = format_registration_confirmation(data)
    
    keyboard = RegistrationKeyboards.get_confirmation()
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "register:confirm")
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    """Confirm and submit registration"""
    try:
        data = await state.get_data()
        data['tg_id'] = str(callback.from_user.id)
        
        # Create teacher via API
        teacher = await api_client.create_teacher(data)
        
        await state.clear()
        
        text = (
            "🎉 <b>Регистрация завершена!</b>\n\n"
            f"Добро пожаловать, {teacher['full_name']}!\n\n"
            "Теперь вы можете пользоваться всеми функциями бота."
        )
        
        keyboard = MainMenuKeyboard.get_keyboard(is_registered=True)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer("✅ Регистрация успешно завершена!")
        
    except APIError as e:
        logger.error(f"Registration API error: {e}")
        await callback.answer("❌ Ошибка при регистрации. Попробуйте позже.", show_alert=True)
    except Exception as e:
        logger.error(f"Registration error: {e}")
        await callback.answer("❌ Произошла ошибка. Попробуйте позже.", show_alert=True)


@router.callback_query(F.data == "register:edit")
async def edit_registration(callback: CallbackQuery):
    """Edit registration data"""
    text = "✏️ <b>Редактирование данных</b>\n\nЧто хотите изменить?"
    keyboard = RegistrationKeyboards.get_edit_field()
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "register:cancel")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    """Cancel registration"""
    await state.clear()
    
    text = (
        "❌ <b>Регистрация отменена</b>\n\n"
        "Вы можете начать регистрацию заново в любое время."
    )
    
    keyboard = MainMenuKeyboard.get_keyboard(is_registered=False)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer("Регистрация отменена")