from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta, timezone
from loguru import logger
from typing import List, Dict, Any

from services.api_client import api_client, APIError
from keyboards.finance import FinanceKeyboards
from keyboards.navigation import NavigationMixin
from utils.formatters import format_invoice_info, format_invoices_list

router = Router()


@router.callback_query(F.data == "finance:dashboard")
async def callback_finance_dashboard(callback: CallbackQuery):
    """Show financial dashboard"""
    try:
        # Check if teacher is registered
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        if not teacher:
            await callback.answer("❌ Вы не зарегистрированы", show_alert=True)
            return
        
        # Get teacher's financial data
        lessons = await api_client.get_lessons(teacher["id"])
        invoices = await api_client.get_invoices_by_teacher(teacher["id"])
        
        # Calculate statistics
        stats = _calculate_financial_stats(lessons, invoices)
        
        text = _format_finance_dashboard(stats)
        keyboard = FinanceKeyboards.get_finance_dashboard()
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error in finance dashboard: {e}")
        await callback.answer("⚠️ Ошибка получения финансовых данных", show_alert=True)


@router.callback_query(F.data == "finance:invoices")
async def callback_finance_invoices(callback: CallbackQuery):
    """Show teacher's invoices"""
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        if not teacher:
            await callback.answer("❌ Вы не зарегистрированы", show_alert=True)
            return
        
        invoices = await api_client.get_invoices_by_teacher(teacher["id"])
        text = format_invoices_list(invoices)
        
        # Add action buttons for recent invoices
        keyboard_buttons = []
        for invoice in invoices[:5]:  # Show max 5 invoices with buttons
            status_emoji = "💳" if invoice["status"] == "unpaid" else "✅"
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{status_emoji} Счет #{invoice['id']}",
                    callback_data=f"invoice:view:{invoice['id']}"
                )
            ])
        
        # Add navigation
        keyboard_buttons.append([
            InlineKeyboardButton(text="⬅️ Финансы", callback_data="finance:dashboard"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="nav:home")
        ])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting invoices: {e}")
        await callback.answer("⚠️ Ошибка получения счетов", show_alert=True)


@router.callback_query(F.data.startswith("invoice:view:"))
async def callback_invoice_view(callback: CallbackQuery):
    """View invoice details"""
    try:
        invoice_id = int(callback.data.split(":")[2])
        
        # Get invoice details (we need to implement this in API client)
        # For now, we'll get it from the invoices list
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        invoices = await api_client.get_invoices_by_teacher(teacher["id"])
        
        invoice = None
        for inv in invoices:
            if inv["id"] == invoice_id:
                invoice = inv
                break
        
        if not invoice:
            await callback.answer("❌ Счет не найден", show_alert=True)
            return
        
        text = format_invoice_info(invoice)
        keyboard = FinanceKeyboards.get_invoice_keyboard(invoice_id, invoice["status"])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting invoice: {e}")
        await callback.answer("⚠️ Ошибка получения счета", show_alert=True)
    except ValueError:
        await callback.answer("❌ Неверный ID счета", show_alert=True)


@router.callback_query(F.data.startswith("invoice:paid:"))
async def callback_invoice_mark_paid(callback: CallbackQuery):
    """Mark invoice as paid"""
    try:
        invoice_id = int(callback.data.split(":")[2])
        
        # Update invoice status
        await api_client.update_invoice_status(invoice_id, "paid")
        
        await callback.answer("✅ Счет отмечен как оплаченный")
        
        # Refresh invoice view
        await callback_invoice_view(callback)
        
    except APIError as e:
        logger.error(f"API error updating invoice status: {e}")
        await callback.answer("⚠️ Ошибка обновления статуса", show_alert=True)
    except ValueError:
        await callback.answer("❌ Неверный ID счета", show_alert=True)


@router.callback_query(F.data == "finance:stats")
async def callback_finance_stats(callback: CallbackQuery):
    """Show detailed financial statistics"""
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        if not teacher:
            await callback.answer("❌ Вы не зарегистрированы", show_alert=True)
            return
        
        lessons = await api_client.get_lessons(teacher["id"])
        invoices = await api_client.get_invoices_by_teacher(teacher["id"])
        
        # Calculate detailed statistics
        stats = _calculate_detailed_stats(lessons, invoices)
        text = _format_detailed_stats(stats)
        
        keyboard_buttons = [
            [InlineKeyboardButton(text="📊 За период", callback_data="earnings:period")],
            [InlineKeyboardButton(text="📈 Тренды", callback_data="finance:trends")]
        ]
        keyboard_buttons = NavigationMixin.add_navigation(keyboard_buttons)
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting financial stats: {e}")
        await callback.answer("⚠️ Ошибка получения статистики", show_alert=True)


@router.callback_query(F.data == "finance:earnings")
async def callback_finance_earnings(callback: CallbackQuery):
    """Show earnings overview"""
    try:
        teacher = await api_client.get_teacher_by_tg_id(str(callback.from_user.id))
        if not teacher:
            await callback.answer("❌ Вы не зарегистрированы", show_alert=True)
            return
        
        lessons = await api_client.get_lessons(teacher["id"])
        
        # Calculate earnings by period
        earnings = _calculate_earnings_by_period(lessons)
        text = _format_earnings_overview(earnings)
        
        keyboard = FinanceKeyboards.get_earnings_period()
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except APIError as e:
        logger.error(f"API error getting earnings: {e}")
        await callback.answer("⚠️ Ошибка получения доходов", show_alert=True)


def _calculate_financial_stats(lessons: List[Dict[str, Any]], invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate financial statistics"""
    confirmed_lessons = [l for l in lessons if l["status"] == "confirmed"]
    unpaid_invoices = [i for i in invoices if i["status"] == "unpaid"]
    paid_invoices = [i for i in invoices if i["status"] == "paid"]
    
    # Calculate lesson values (we need to get actual values from lessons)
    total_confirmed_value = sum(float(lesson["price"]) for lesson in confirmed_lessons)
    
    # This month's lessons
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month_lessons = []
    
    for lesson in confirmed_lessons:
        lesson_date = datetime.fromisoformat(lesson['date_time'].replace('Z', '+00:00'))
        if lesson_date >= month_start:
            this_month_lessons.append(lesson)
    
    this_month_value = sum(float(lesson["price"]) for lesson in this_month_lessons)
    
    return {
        "total_lessons": len(lessons),
        "confirmed_lessons": len(confirmed_lessons),
        "total_confirmed_value": total_confirmed_value,
        "this_month_lessons": len(this_month_lessons),
        "this_month_value": this_month_value,
        "unpaid_invoices": len(unpaid_invoices),
        "paid_invoices": len(paid_invoices),
        "total_invoices": len(invoices)
    }


def _format_finance_dashboard(stats: Dict[str, Any]) -> str:
    """Format financial dashboard"""
    text = "💰 <b>Финансовая панель</b>\n\n"
    
    text += f"📊 <b>Общая статистика:</b>\n"
    text += f"✅ Подтвержденных уроков: {stats['confirmed_lessons']}\n"
    text += f"💰 Общая сумма: {stats['total_confirmed_value']:,.0f} ₽\n\n"
    
    text += f"📅 <b>За текущий месяц:</b>\n"
    text += f"📚 Уроков: {stats['this_month_lessons']}\n"
    text += f"💵 Доход: {stats['this_month_value']:,.0f} ₽\n\n"
    
    text += f"💳 <b>Счета:</b>\n"
    text += f"⏳ Неоплачено: {stats['unpaid_invoices']}\n"
    text += f"✅ Оплачено: {stats['paid_invoices']}\n"
    
    return text


def _calculate_detailed_stats(lessons: List[Dict[str, Any]], invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate detailed financial statistics"""
    # Group lessons by status
    lesson_stats = {"planned": 0, "confirmed": 0, "cancelled": 0}
    lesson_values = {"planned": 0, "confirmed": 0, "cancelled": 0}
    
    for lesson in lessons:
        status = lesson["status"]
        lesson_stats[status] += 1
        lesson_values[status] += float(lesson["price"])
    
    # Calculate average lesson price
    avg_price = lesson_values["confirmed"] / max(lesson_stats["confirmed"], 1)
    
    # Payment rate
    payment_rate = (len([i for i in invoices if i["status"] == "paid"]) / max(len(invoices), 1)) * 100
    
    return {
        "lesson_stats": lesson_stats,
        "lesson_values": lesson_values,
        "avg_price": avg_price,
        "payment_rate": payment_rate
    }


def _format_detailed_stats(stats: Dict[str, Any]) -> str:
    """Format detailed statistics"""
    text = "📈 <b>Подробная статистика</b>\n\n"
    
    text += f"📚 <b>Уроки по статусам:</b>\n"
    text += f"📅 Запланировано: {stats['lesson_stats']['planned']}\n"
    text += f"✅ Подтверждено: {stats['lesson_stats']['confirmed']}\n"
    text += f"❌ Отменено: {stats['lesson_stats']['cancelled']}\n\n"
    
    text += f"💰 <b>Финансовые показатели:</b>\n"
    text += f"💵 Средняя цена урока: {stats['avg_price']:,.0f} ₽\n"
    text += f"📊 Процент оплат: {stats['payment_rate']:.1f}%\n\n"
    
    text += f"🎯 <b>Доходы по статусам:</b>\n"
    text += f"✅ Подтверждено: {stats['lesson_values']['confirmed']:,.0f} ₽\n"
    text += f"⏳ В ожидании: {stats['lesson_values']['planned']:,.0f} ₽\n"
    
    return text


def _calculate_earnings_by_period(lessons: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate earnings by different periods"""
    now = datetime.now(timezone.utc)
    
    # This month
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # This week
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    periods = {
        "this_month": {"start": month_start, "lessons": [], "value": 0},
        "this_week": {"start": week_start, "lessons": [], "value": 0},
        "last_30_days": {"start": now - timedelta(days=30), "lessons": [], "value": 0}
    }
    
    for lesson in lessons:
        if lesson["status"] != "confirmed":
            continue
            
        lesson_date = datetime.fromisoformat(lesson['date_time'].replace('Z', '+00:00'))
        lesson_value = float(lesson["price"])
        
        for period_name, period_data in periods.items():
            if lesson_date >= period_data["start"]:
                period_data["lessons"].append(lesson)
                period_data["value"] += lesson_value
    
    return periods


def _format_earnings_overview(earnings: Dict[str, Any]) -> str:
    """Format earnings overview"""
    text = "💵 <b>Обзор доходов</b>\n\n"
    
    text += f"📅 <b>За текущий месяц:</b>\n"
    text += f"💰 {earnings['this_month']['value']:,.0f} ₽\n"
    text += f"📚 {len(earnings['this_month']['lessons'])} уроков\n\n"
    
    text += f"📊 <b>За неделю:</b>\n"
    text += f"💰 {earnings['this_week']['value']:,.0f} ₽\n"
    text += f"📚 {len(earnings['this_week']['lessons'])} уроков\n\n"
    
    text += f"🗓️ <b>За последние 30 дней:</b>\n"
    text += f"💰 {earnings['last_30_days']['value']:,.0f} ₽\n"
    text += f"📚 {len(earnings['last_30_days']['lessons'])} уроков\n"
    
    # Calculate daily average for last 30 days
    daily_avg = earnings['last_30_days']['value'] / 30
    text += f"📈 Среднедневной доход: {daily_avg:,.0f} ₽\n"
    
    return text


