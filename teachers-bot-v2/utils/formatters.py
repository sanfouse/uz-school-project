from datetime import datetime, date
from typing import Dict, List, Any, Optional


def format_welcome_message(teacher_name: str) -> str:
    """Format welcome message for registered teacher"""
    return (
        f"👋 <b>Привет, {teacher_name}!</b>\n\n"
        f"Добро пожаловать в систему управления уроками.\n"
        f"Выберите нужный раздел в меню ниже."
    )


def format_teacher_profile(teacher: Dict[str, Any]) -> str:
    """Format teacher profile information"""
    text = f"👤 <b>Профиль учителя</b>\n\n"
    text += f"📝 <b>Имя:</b> {teacher['full_name']}\n"
    
    if teacher.get('phone'):
        text += f"📞 <b>Телефон:</b> {teacher['phone']}\n"
    
    if teacher.get('email'):
        text += f"📧 <b>Email:</b> {teacher['email']}\n"
    
    text += f"🏦 <b>Банковский счет:</b> {teacher['bank_account'][:4]}****{teacher['bank_account'][-4:]}\n"
    text += f"🆔 <b>Telegram ID:</b> {teacher['tg_id']}\n"
    
    return text


def format_lesson_info(lesson: Dict[str, Any]) -> str:
    """Format lesson information"""
    # Parse datetime
    lesson_datetime = datetime.fromisoformat(lesson['date_time'].replace('Z', '+00:00'))
    
    # Status emoji
    status_emoji = {
        'planned': '📅',
        'confirmed': '✅', 
        'cancelled': '❌'
    }.get(lesson['status'], '❓')
    
    # Type emoji
    type_emoji = {
        'trial': '🎯',
        'regular': '📚'
    }.get(lesson['type'], '📝')
    
    text = f"📚 <b>Урок #{lesson['id']}</b>\n\n"
    text += f"👤 <b>Студент:</b> {lesson['student_name']}\n"
    text += f"📅 <b>Дата:</b> {lesson_datetime.strftime('%d.%m.%Y')}\n"
    text += f"⏰ <b>Время:</b> {lesson_datetime.strftime('%H:%M')}\n"
    text += f"💰 <b>Цена:</b> {lesson['price']} ₽\n"
    text += f"{status_emoji} <b>Статус:</b> {lesson['status']}\n"
    text += f"{type_emoji} <b>Тип:</b> {lesson['type']}\n"
    
    return text


def format_lessons_list(lessons: List[Dict[str, Any]], title: str = "Уроки") -> str:
    """Format list of lessons"""
    if not lessons:
        return f"📚 <b>{title}</b>\n\nУроков не найдено."
    
    text = f"📚 <b>{title}</b>\n\n"
    
    for lesson in lessons:
        lesson_datetime = datetime.fromisoformat(lesson['date_time'].replace('Z', '+00:00'))
        status_emoji = {
            'planned': '📅',
            'confirmed': '✅',
            'cancelled': '❌'
        }.get(lesson['status'], '❓')
        
        text += (
            f"{status_emoji} <b>#{lesson['id']}</b> - {lesson['student_name']}\n"
            f"📅 {lesson_datetime.strftime('%d.%m.%Y %H:%M')} | 💰 {lesson['price']} ₽\n"
            f"{'─' * 30}\n"
        )
    
    text += f"\n<b>Всего уроков:</b> {len(lessons)}"
    return text


def format_invoice_info(invoice: Dict[str, Any]) -> str:
    """Format invoice information"""
    created_at = datetime.fromisoformat(invoice['created_at'].replace('Z', '+00:00'))
    
    status_emoji = {
        'unpaid': '💳',
        'paid': '✅'
    }.get(invoice['status'], '❓')
    
    text = f"💳 <b>Счет #{invoice['id']}</b>\n\n"
    text += f"📚 <b>Урок:</b> #{invoice['lesson_id']}\n"
    text += f"📅 <b>Создан:</b> {created_at.strftime('%d.%m.%Y %H:%M')}\n"
    text += f"{status_emoji} <b>Статус:</b> {invoice['status']}\n"
    text += f"🏦 <b>T-Bank ID:</b> {invoice['tbank_invoice_id']}\n"
    text += f"📄 <b>Реквизиты:</b> <a href='{invoice['pdf_url']}'>Скачать</a>\n"
    
    return text


def format_invoices_list(invoices: List[Dict[str, Any]]) -> str:
    """Format list of invoices"""
    if not invoices:
        return "💳 <b>Счета</b>\n\nСчетов не найдено."
    
    text = "💳 <b>Мои счета</b>\n\n"
    
    total_unpaid = 0
    total_paid = 0
    
    for invoice in invoices:
        created_at = datetime.fromisoformat(invoice['created_at'].replace('Z', '+00:00'))
        status_emoji = {
            'unpaid': '💳',
            'paid': '✅'
        }.get(invoice['status'], '❓')
        
        text += (
            f"{status_emoji} <b>#{invoice['id']}</b>\n"
            f"📅 {created_at.strftime('%d.%m.%Y')} | Урок #{invoice['lesson_id']}\n"
            f"{'─' * 25}\n"
        )
        
        # Count totals (would need lesson info for amounts)
        if invoice['status'] == 'unpaid':
            total_unpaid += 1
        else:
            total_paid += 1
    
    text += f"\n📊 <b>Статистика:</b>\n"
    text += f"💳 Неоплачено: {total_unpaid}\n"
    text += f"✅ Оплачено: {total_paid}\n"
    
    return text


def format_registration_confirmation(data: Dict[str, Any]) -> str:
    """Format registration confirmation"""
    text = "📝 <b>Подтверждение регистрации</b>\n\n"
    text += f"👤 <b>Имя:</b> {data['full_name']}\n"
    
    if data.get('phone'):
        text += f"📞 <b>Телефон:</b> {data['phone']}\n"
    
    if data.get('email'):
        text += f"📧 <b>Email:</b> {data['email']}\n"
    
    text += f"🏦 <b>Банковский счет:</b> {data['bank_account']}\n"
    text += f"\nВсе данные корректны?"
    
    return text


def format_today_date() -> str:
    """Format today's date"""
    return date.today().strftime('%d.%m.%Y')


def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime('%d.%m.%Y %H:%M')