import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid Russian phone number
    if len(digits_only) == 11 and digits_only.startswith('7'):
        return True
    elif len(digits_only) == 10 and digits_only.startswith('9'):
        return True
    elif len(digits_only) >= 10 and len(digits_only) <= 15:
        return True
    
    return False


def validate_bank_account(account: str) -> bool:
    """Validate bank account number"""
    if not account:
        return False
    
    # Remove spaces and other characters
    clean_account = re.sub(r'\s+', '', account)
    
    # Check if it's all digits and has appropriate length
    if re.match(r'^\d{20}$', clean_account):
        return True
    
    # Also accept shorter formats (some banks use different lengths)
    if re.match(r'^\d{16,20}$', clean_account):
        return True
    
    return False


def validate_price(price_str: str) -> Optional[float]:
    """Validate and convert price string to float"""
    try:
        price = float(price_str.replace(',', '.'))
        if price > 0:
            return price
        return None
    except (ValueError, TypeError):
        return None


def validate_lesson_date(date_str: str) -> bool:
    """Validate date format DD.MM.YYYY"""
    pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    return re.match(pattern, date_str) is not None


def validate_lesson_time(time_str: str) -> bool:
    """Validate time format HH:MM"""
    pattern = r'^\d{2}:\d{2}$'
    if not re.match(pattern, time_str):
        return False
    
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    
    return 0 <= hours <= 23 and 0 <= minutes <= 59


def sanitize_input(text: str, max_length: int = 255) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = text.strip()
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    return text