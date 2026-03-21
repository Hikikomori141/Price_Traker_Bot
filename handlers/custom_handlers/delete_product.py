from loader import bot, logger
from database.db_manager import Session, Product
from telebot.types import CallbackQuery


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_prod_'))
def handle_delete_product(call: CallbackQuery) -> None:
    """
    Ловит нажатие на кнопку удаления, удаляет запись из БД и убирает сообщение.
    """
    product_id = int(call.data.replace('delete_prod_', ''))
    session = Session()

    try:
        product = session.query(Product).filter_by(id=product_id).first()

        if product:
            title = product.title
            session.delete(product)
            session.commit()

            # Уведомляем пользователя
            bot.answer_callback_query(call.id, f"Товар удален: {title}")

            # Удаляем само сообщение с товаром из чата
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "⚠️ Товар уже удален или не найден.")

    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при удалении товара {product_id}: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "❌ Произошла ошибка при удалении.")
    finally:
        session.close()