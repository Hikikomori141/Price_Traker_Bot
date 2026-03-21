from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_delete_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Создает инлайн-кнопку удаления для конкретного товара.
    """
    keyboard = InlineKeyboardMarkup()

    delete_button = InlineKeyboardButton(
        text="❌ Удалить из списка",
        callback_data=f"delete_prod_{product_id}"
    )
    keyboard.add(delete_button)
    return keyboard