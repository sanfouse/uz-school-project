from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from datetime import datetime, date, time
from loguru import logger

from models.states import LessonStates
from services.api_client import api_client, APIError
from keyboards.lessons import LessonKeyboards
from keyboards.navigation import MainMenuKeyboard
from utils.formatters import format_lesson_info, format_lessons_list, format_today_date
from utils.validators import validate_price, validate_lesson_date, validate_lesson_time

router = Router()


@router.callback_query(F.data == "lessons:menu")
async def callback_lessons_menu(callback: CallbackQuery):
    """Show lessons menu"""
    try:
        # Check if teacher is registered
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        if not teacher:
            await callback.answer("❌ Вы не зарегистрированы", show_alert=True)
            return
        
        text = "📚 <b>Управление уроками</b>\n\nВыберите действие:"
        keyboard = LessonKeyboards.get_lessons_menu()
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error in lessons menu: {e}")
        await callback.answer("⚠️ Ошибка подключения к серверу", show_alert=True)


@router.callback_query(F.data == "lessons:list")
async def callback_lessons_list(callback: CallbackQuery):
    """Show all lessons"""
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        if not teacher:
            await callback.answer("❌ Вы не зарегистрированы", show_alert=True)
            return
        
        lessons = await api_client.get_lessons(teacher["id"])
        text = format_lessons_list(lessons, "Все уроки")
        
        # Add action buttons for each lesson
        keyboard_buttons = []
        for lesson in lessons[:5]:  # Show max 5 lessons with buttons
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"▶️ Урок #{lesson['id']} - {lesson['student_name']}",
                    callback_data=f"lesson:view:{lesson['id']}"
                )
            ])
        
        # Add navigation
        keyboard_buttons.extend([
            [InlineKeyboardButton(text="➕ Создать урок", callback_data="lesson:create")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="lessons:menu")]
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting lessons: {e}")
        await callback.answer("⚠️ Ошибка получения уроков", show_alert=True)


@router.callback_query(F.data == "lessons:today")
async def callback_lessons_today(callback: CallbackQuery):
    """Show today's lessons"""
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        if not teacher:
            await callback.answer("❌ Вы не зарегистрированы", show_alert=True)
            return
        
        # Get all lessons and filter for today
        all_lessons = await api_client.get_lessons(teacher["id"])
        today = date.today()
        today_lessons = []
        
        for lesson in all_lessons:
            lesson_date = datetime.fromisoformat(lesson['date_time'].replace('Z', '+00:00')).date()
            if lesson_date == today:
                today_lessons.append(lesson)
        
        text = format_lessons_list(today_lessons, f"Уроки на {format_today_date()}")
        
        # Add quick actions for today's lessons
        keyboard_buttons = []
        for lesson in today_lessons[:3]:  # Max 3 lessons with buttons
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"▶️ {lesson['student_name']} в {datetime.fromisoformat(lesson['date_time'].replace('Z', '+00:00')).strftime('%H:%M')}",
                    callback_data=f"lesson:view:{lesson['id']}"
                )
            ])
        
        keyboard_buttons.extend([
            [InlineKeyboardButton(text="📚 Все уроки", callback_data="lessons:list")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="lessons:menu")]
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting today's lessons: {e}")
        await callback.answer("⚠️ Ошибка получения уроков", show_alert=True)


@router.callback_query(F.data == "lessons:week")
async def callback_lessons_week(callback: CallbackQuery):
    """Show this week's lessons"""
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        if not teacher:
            await callback.answer("❌ Вы не зарегистрированы", show_alert=True)
            return
        
        # Get all lessons and filter for this week
        from datetime import datetime, timedelta, timezone
        all_lessons = await api_client.get_lessons(teacher["id"])
        
        # Calculate week start (Monday) and end (Sunday)
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)
        
        week_lessons = []
        for lesson in all_lessons:
            lesson_date = datetime.fromisoformat(lesson['date_time'].replace('Z', '+00:00'))
            if week_start <= lesson_date < week_end:
                week_lessons.append(lesson)
        
        # Sort by date
        week_lessons.sort(key=lambda x: x['date_time'])
        
        text = format_lessons_list(week_lessons, f"Уроки на неделю ({week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m')})")
        
        # Add quick actions for week lessons
        keyboard_buttons = []
        for lesson in week_lessons[:3]:  # Max 3 lessons with buttons
            lesson_dt = datetime.fromisoformat(lesson['date_time'].replace('Z', '+00:00'))
            day_name = {0: 'Пн', 1: 'Вт', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Вс'}[lesson_dt.weekday()]
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"▶️ {day_name} {lesson['student_name']} {lesson_dt.strftime('%H:%M')}",
                    callback_data=f"lesson:view:{lesson['id']}"
                )
            ])
        
        keyboard_buttons.extend([
            [InlineKeyboardButton(text="📚 Все уроки", callback_data="lessons:list")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="lessons:menu")]
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting week's lessons: {e}")
        await callback.answer("⚠️ Ошибка получения уроков", show_alert=True)


@router.callback_query(F.data.startswith("lesson:view:"))
async def callback_lesson_view(callback: CallbackQuery):
    """View lesson details"""
    try:
        lesson_id = int(callback.data.split(":")[2])
        lesson = await api_client.get_lesson(lesson_id)
        
        text = format_lesson_info(lesson)
        keyboard = LessonKeyboards.get_lesson_detail_keyboard(lesson_id, lesson["status"])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting lesson: {e}")
        await callback.answer("⚠️ Ошибка получения урока", show_alert=True)
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)


@router.callback_query(F.data.startswith("lesson:confirm:"))
async def callback_lesson_confirm(callback: CallbackQuery):
    """Confirm lesson"""
    try:
        lesson_id = int(callback.data.split(":")[2])
        
        # Confirm lesson via API
        await api_client.confirm_lesson(lesson_id)
        
        await callback.answer("✅ Урок подтвержден! Счет будет создан автоматически.")
        
        # Refresh lesson view
        lesson = await api_client.get_lesson(lesson_id)
        text = format_lesson_info(lesson)
        keyboard = LessonKeyboards.get_lesson_detail_keyboard(lesson_id, lesson["status"])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        
    except APIError as e:
        logger.error(f"API error confirming lesson: {e}")
        await callback.answer("⚠️ Ошибка подтверждения урока", show_alert=True)
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)


@router.callback_query(F.data.startswith("lesson:cancel:"))
async def callback_lesson_cancel(callback: CallbackQuery):
    """Cancel lesson"""
    try:
        lesson_id = int(callback.data.split(":")[2])
        
        # Update lesson status to cancelled
        await api_client.update_lesson(lesson_id, {"status": "cancelled"})
        
        await callback.answer("❌ Урок отменен")
        
        # Refresh lesson view
        lesson = await api_client.get_lesson(lesson_id)
        text = format_lesson_info(lesson)
        keyboard = LessonKeyboards.get_lesson_detail_keyboard(lesson_id, lesson["status"])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        
    except APIError as e:
        logger.error(f"API error cancelling lesson: {e}")
        await callback.answer("⚠️ Ошибка отмены урока", show_alert=True)
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)


@router.callback_query(F.data == "lesson:create")
async def callback_lesson_create(callback: CallbackQuery, state: FSMContext):
    """Start lesson creation"""
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        if not teacher:
            await callback.answer("❌ Вы не зарегистрированы", show_alert=True)
            return
        
        await state.set_state(LessonStates.waiting_for_student_name)
        await state.update_data(teacher_id=teacher["id"])
        
        text = (
            "➕ <b>Создание урока</b>\n\n"
            "👤 <b>Шаг 1 из 5</b>\n"
            "Введите имя студента:"
        )
        
        await callback.message.edit_text(text)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error starting lesson creation: {e}")
        await callback.answer("⚠️ Ошибка подключения к серверу", show_alert=True)


@router.message(LessonStates.waiting_for_student_name)
async def process_student_name(message: Message, state: FSMContext):
    """Process student name input"""
    student_name = message.text.strip()
    
    if len(student_name) < 2:
        await message.answer("❌ Имя студента слишком короткое. Попробуйте еще раз:")
        return
    
    await state.update_data(student_name=student_name)
    await state.set_state(LessonStates.waiting_for_price)
    
    text = (
        f"💰 <b>Шаг 2 из 5</b>\n"
        f"Студент: {student_name}\n\n"
        f"Введите стоимость урока в рублях:"
    )
    
    await message.answer(text)


@router.message(LessonStates.waiting_for_price)
async def process_price(message: Message, state: FSMContext):
    """Process price input"""
    price = validate_price(message.text.strip())
    
    if price is None:
        await message.answer("❌ Неверная цена. Введите число больше 0:")
        return
    
    await state.update_data(price=price)
    await state.set_state(LessonStates.waiting_for_date)
    
    text = (
        f"📅 <b>Шаг 3 из 5</b>\n"
        f"Цена: {price} ₽\n\n"
        f"Введите дату урока в формате ДД.ММ.ГГГГ:\n"
        f"<i>Например: {format_today_date()}</i>"
    )
    
    await message.answer(text)


@router.message(LessonStates.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    """Process date input"""
    date_str = message.text.strip()
    
    if not validate_lesson_date(date_str):
        await message.answer("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ:")
        return
    
    try:
        lesson_date = datetime.strptime(date_str, "%d.%m.%Y").date()
        # Store as ISO string for JSON serialization
        await state.update_data(lesson_date=lesson_date.isoformat())
        await state.set_state(LessonStates.waiting_for_time)
        
        text = (
            f"⏰ <b>Шаг 4 из 5</b>\n"
            f"Дата: {lesson_date.strftime('%d.%m.%Y')}\n\n"
            f"Введите время урока в формате ЧЧ:ММ:\n"
            f"<i>Например: 14:30</i>"
        )
        
        await message.answer(text)
        
    except ValueError:
        await message.answer("❌ Неверная дата. Попробуйте еще раз:")


@router.message(LessonStates.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    """Process time input"""
    time_str = message.text.strip()
    
    if not validate_lesson_time(time_str):
        await message.answer("❌ Неверный формат времени. Используйте ЧЧ:ММ:")
        return
    
    try:
        lesson_time = datetime.strptime(time_str, "%H:%M").time()
        # Store as string for JSON serialization
        await state.update_data(lesson_time=lesson_time.isoformat())
        await state.set_state(LessonStates.waiting_for_type)
        
        text = (
            f"📝 <b>Шаг 5 из 5</b>\n"
            f"Время: {lesson_time.strftime('%H:%M')}\n\n"
            f"Выберите тип урока:"
        )
        
        keyboard = LessonKeyboards.get_lesson_type_keyboard()
        await message.answer(text, reply_markup=keyboard)
        
    except ValueError:
        await message.answer("❌ Неверное время. Попробуйте еще раз:")


@router.callback_query(F.data.startswith("lesson:type:"), LessonStates.waiting_for_type)
async def process_lesson_type(callback: CallbackQuery, state: FSMContext):
    """Process lesson type selection and create lesson"""
    try:
        lesson_type = callback.data.split(":")[2]  # "trial" or "regular"
        data = await state.get_data()
        
        # Parse date and time from stored strings
        lesson_date = datetime.fromisoformat(data["lesson_date"]).date()
        lesson_time = datetime.strptime(data["lesson_time"], "%H:%M:%S").time()
        
        # Combine date and time
        lesson_datetime = datetime.combine(lesson_date, lesson_time)
        
        # Prepare lesson data
        lesson_data = {
            "student_name": data["student_name"],
            "teacher_id": data["teacher_id"],
            "price": data["price"],
            "date_time": lesson_datetime.isoformat(),
            "type": lesson_type
        }
        
        # Create lesson via API
        lesson = await api_client.create_lesson(lesson_data)
        
        await state.clear()
        
        text = (
            f"✅ <b>Урок создан успешно!</b>\n\n"
            f"🆔 <b>ID урока:</b> {lesson['id']}\n"
            f"👤 <b>Студент:</b> {lesson['student_name']}\n"
            f"📅 <b>Дата:</b> {lesson_datetime.strftime('%d.%m.%Y %H:%M')}\n"
            f"💰 <b>Цена:</b> {lesson['price']} ₽\n"
            f"📝 <b>Тип:</b> {lesson['type']}"
        )
        
        keyboard = LessonKeyboards.get_lesson_detail_keyboard(lesson['id'], lesson['status'])
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer("✅ Урок создан!")
        
    except APIError as e:
        logger.error(f"API error creating lesson: {e}")
        await callback.answer("⚠️ Ошибка создания урока", show_alert=True)
    except Exception as e:
        logger.error(f"Error creating lesson: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


# Handler for lesson confirmation notifications from lesson-checker
@router.callback_query(F.data.startswith("confirm:lesson:"))
async def callback_confirm_lesson_notification(callback: CallbackQuery):
    """Handle lesson confirmation from notification"""
    try:
        lesson_id = int(callback.data.split(":")[2])
        
        # Confirm lesson via API
        await api_client.confirm_lesson(lesson_id)
        
        text = (
            f"✅ <b>Урок #{lesson_id} подтвержден!</b>\n\n"
            f"Счет будет создан автоматически и отправлен на оплату."
        )
        
        await callback.message.edit_text(text)
        await callback.answer("✅ Урок подтвержден!")
        
    except APIError as e:
        logger.error(f"API error confirming lesson from notification: {e}")
        await callback.answer("⚠️ Ошибка подтверждения урока", show_alert=True)
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)


@router.callback_query(F.data.startswith("cancel:lesson:"))
async def callback_cancel_lesson_notification(callback: CallbackQuery):
    """Handle lesson cancellation from notification"""
    try:
        lesson_id = int(callback.data.split(":")[2])
        
        # Cancel lesson via API
        await api_client.update_lesson(lesson_id, {"status": "cancelled"})
        
        text = (
            f"❌ <b>Урок #{lesson_id} отменен</b>\n\n"
            f"Информация о несостоявшемся уроке сохранена."
        )
        
        await callback.message.edit_text(text)
        await callback.answer("❌ Урок отменен")
        
    except APIError as e:
        logger.error(f"API error cancelling lesson from notification: {e}")
        await callback.answer("⚠️ Ошибка отмены урока", show_alert=True)
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)


@router.callback_query(F.data.regexp(r"^lesson:edit:\d+$"))
async def callback_lesson_edit_menu(callback: CallbackQuery):
    """Show lesson edit menu"""
    try:
        lesson_id = int(callback.data.split(":")[2])
        lesson = await api_client.get_lesson(lesson_id)
        
        text = (
            f"✏️ <b>Редактирование урока #{lesson_id}</b>\n\n"
            f"{format_lesson_info(lesson)}\n\n"
            f"Что хотите изменить?"
        )
        
        keyboard = LessonKeyboards.get_lesson_edit_keyboard(lesson_id)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting lesson for edit: {e}")
        await callback.answer("⚠️ Ошибка получения урока", show_alert=True)
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)


@router.callback_query(F.data.startswith("lesson:edit:name:"))
async def callback_lesson_edit_name(callback: CallbackQuery, state: FSMContext):
    """Start editing lesson student name"""
    try:
        lesson_id = int(callback.data.split(":")[3])
        
        await state.set_state(LessonStates.editing_student_name)
        await state.update_data(lesson_id=lesson_id)
        
        text = (
            f"👤 <b>Изменение имени студента</b>\n"
            f"Урок #{lesson_id}\n\n"
            f"Введите новое имя студента:"
        )
        
        await callback.message.edit_text(text)
        await callback.answer()
        
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)


@router.message(LessonStates.editing_student_name)
async def process_lesson_name_edit(message: Message, state: FSMContext):
    """Process lesson name edit"""
    try:
        new_name = message.text.strip()
        
        if len(new_name) < 2:
            await message.answer("❌ Имя студента слишком короткое. Попробуйте еще раз:")
            return
        
        data = await state.get_data()
        lesson_id = data["lesson_id"]
        
        # Update lesson via API
        await api_client.update_lesson(lesson_id, {"student_name": new_name})
        
        await state.clear()
        
        text = f"✅ <b>Имя студента изменено!</b>\n\nНовое имя: {new_name}"
        
        # Show updated lesson
        lesson = await api_client.get_lesson(lesson_id)
        text = format_lesson_info(lesson)
        keyboard = LessonKeyboards.get_lesson_detail_keyboard(lesson_id, lesson["status"])
        
        await message.answer(text, reply_markup=keyboard)
        
    except APIError as e:
        logger.error(f"API error updating lesson name: {e}")
        await message.answer("⚠️ Ошибка при обновлении имени студента")
        await state.clear()


@router.callback_query(F.data.startswith("lesson:edit:price:"))
async def callback_lesson_edit_price(callback: CallbackQuery, state: FSMContext):
    """Start editing lesson price"""
    try:
        lesson_id = int(callback.data.split(":")[3])
        
        await state.set_state(LessonStates.editing_price)
        await state.update_data(lesson_id=lesson_id)
        
        text = (
            f"💰 <b>Изменение цены урока</b>\n"
            f"Урок #{lesson_id}\n\n"
            f"Введите новую цену в рублях:"
        )
        
        await callback.message.edit_text(text)
        await callback.answer()
        
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)


@router.message(LessonStates.editing_price)
async def process_lesson_price_edit(message: Message, state: FSMContext):
    """Process lesson price edit"""
    try:
        price = validate_price(message.text.strip())
        
        if price is None:
            await message.answer("❌ Неверная цена. Введите число больше 0:")
            return
        
        data = await state.get_data()
        lesson_id = data["lesson_id"]
        
        # Update lesson via API
        await api_client.update_lesson(lesson_id, {"price": price})
        
        await state.clear()
        
        # Show updated lesson
        lesson = await api_client.get_lesson(lesson_id)
        text = format_lesson_info(lesson)
        keyboard = LessonKeyboards.get_lesson_detail_keyboard(lesson_id, lesson["status"])
        
        await message.answer(text, reply_markup=keyboard)
        
    except APIError as e:
        logger.error(f"API error updating lesson price: {e}")
        await message.answer("⚠️ Ошибка при обновлении цены")
        await state.clear()


@router.callback_query(F.data.regexp(r"^lesson:delete:\d+$"))
async def callback_lesson_delete(callback: CallbackQuery):
    """Delete lesson with confirmation"""
    try:
        lesson_id = int(callback.data.split(":")[2])
        
        text = (
            f"🗑️ <b>Удаление урока #{lesson_id}</b>\n\n"
            f"⚠️ <b>Внимание!</b> Это действие нельзя отменить.\n\n"
            f"Вы уверены, что хотите удалить урок?"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"lesson:delete:confirm:{lesson_id}"),
                InlineKeyboardButton(text="❌ Отмена", callback_data=f"lesson:view:{lesson_id}")
            ]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)


@router.callback_query(F.data.startswith("lesson:delete:confirm:"))
async def callback_lesson_delete_confirm(callback: CallbackQuery):
    """Confirm lesson deletion"""
    try:
        lesson_id = int(callback.data.split(":")[3])
        
        # Delete lesson via API
        await api_client.delete_lesson(lesson_id)
        
        text = (
            f"✅ <b>Урок #{lesson_id} удален</b>\n\n"
            f"Урок успешно удален из системы."
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 К списку уроков", callback_data="lessons:list")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="nav:home")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer("✅ Урок удален")
        
    except APIError as e:
        logger.error(f"API error deleting lesson: {e}")
        await callback.answer("⚠️ Ошибка удаления урока", show_alert=True)
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)


@router.callback_query(F.data.startswith("lesson:student:"))
async def callback_lesson_student(callback: CallbackQuery):
    """Show student information for lesson"""
    try:
        lesson_id = int(callback.data.split(":")[2])
        lesson = await api_client.get_lesson(lesson_id)
        
        text = (
            f"👤 <b>Информация о студенте</b>\n\n"
            f"📚 <b>Урок #{lesson_id}</b>\n"
            f"👤 <b>Студент:</b> {lesson['student_name']}\n"
            f"💰 <b>Цена урока:</b> {lesson['price']} ₽\n"
            f"📝 <b>Тип:</b> {lesson['type']}\n\n"
            f"<i>Дополнительная информация о студенте будет добавлена в будущих версиях.</i>"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ К уроку", callback_data=f"lesson:view:{lesson_id}")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="nav:home")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting lesson student info: {e}")
        await callback.answer("⚠️ Ошибка получения информации", show_alert=True)
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)


@router.callback_query(F.data.startswith("lesson:invoice:"))
async def callback_lesson_invoice(callback: CallbackQuery):
    """Show invoice for lesson"""
    try:
        lesson_id = int(callback.data.split(":")[2])
        
        # Try to get invoice for this lesson
        try:
            invoice = await api_client.get_invoice_by_lesson(lesson_id)
            
            from utils.formatters import format_invoice_info
            text = format_invoice_info(invoice)
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💰 Финансы", callback_data="finance:dashboard")],
                [InlineKeyboardButton(text="⬅️ К уроку", callback_data=f"lesson:view:{lesson_id}")]
            ])
            
        except APIError:
            # No invoice found for this lesson
            lesson = await api_client.get_lesson(lesson_id)
            
            if lesson["status"] == "confirmed":
                text = (
                    f"💳 <b>Счет для урока #{lesson_id}</b>\n\n"
                    f"Счет для этого урока создается автоматически.\n"
                    f"Если счет не создан, обратитесь к администратору."
                )
            else:
                text = (
                    f"💳 <b>Счет для урока #{lesson_id}</b>\n\n"
                    f"Счет будет создан автоматически после подтверждения урока.\n"
                    f"Статус урока: {lesson['status']}"
                )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ К уроку", callback_data=f"lesson:view:{lesson_id}")]
            ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting lesson invoice: {e}")
        await callback.answer("⚠️ Ошибка получения счета", show_alert=True)
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)


@router.callback_query(F.data.startswith("lesson:details:"))
async def callback_lesson_details(callback: CallbackQuery):
    """Show lesson details (from notification)"""
    try:
        lesson_id = int(callback.data.split(":")[2])
        lesson = await api_client.get_lesson(lesson_id)
        
        text = format_lesson_info(lesson)
        keyboard = LessonKeyboards.get_lesson_detail_keyboard(lesson_id, lesson["status"])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting lesson details: {e}")
        await callback.answer("⚠️ Ошибка получения урока", show_alert=True)
    except ValueError:
        await callback.answer("❌ Неверный ID урока", show_alert=True)