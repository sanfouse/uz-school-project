from src.orders.schema import Order
from core.util import _load_words


async def is_valid_order(order: Order):
    words = _load_words()
    
    if not words:
        return True
        
    if any(bad_word.lower() in order.subject.lower() for bad_word in words):
        return False
    if any(
            bad_word.lower() in order.description.lower() for bad_word in words
    ):
        return False
    return True
