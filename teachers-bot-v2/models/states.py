from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """States for teacher registration process"""
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_bank_account = State()
    confirmation = State()


class LessonStates(StatesGroup):
    """States for lesson management"""
    waiting_for_student_name = State()
    waiting_for_price = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_type = State()
    
    # Edit states
    editing_student_name = State()
    editing_price = State()
    editing_date = State()
    editing_time = State()


class ProfileStates(StatesGroup):
    """States for profile editing"""
    editing_name = State()
    editing_phone = State()
    editing_email = State()
    editing_bank_account = State()