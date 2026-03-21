from telebot.types import Message
from loader import bot, logger
from database.db_manager import Session, User
from keyboards.inline_keyboards import get_delete_keyboard


@bot.message_handler(commands=['my_products'])
def show_my_products(message: Message) -> None:
    """
    Выводит список всех товаров, которые отслеживает конкретный пользователь.
    Если товаров нет — отправляет соответствующее сообщение.
    """
    session = Session()
    try:
        # Ищем пользователя в БД по его Telegram ID
        user = session.query(User).filter_by(user_id=message.from_user.id).first()

        # Если пользователя нет в базе или у него пустой список товаров
        if not user or not user.products:
            bot.reply_to(
                message,
                "📂 <b>У вас пока нет отслеживаемых товаров.</b>\n"
                "Просто пришлите мне ссылку на товар Wildberries!",
                parse_mode="HTML"
            )
            return

        bot.send_message(message.chat.id, "📋 <b>Ваш список отслеживания:</b>", parse_mode="HTML")

        for product in user.products:
            price_val = f"<b>{product.current_price} BYN</b>" if product.current_price else "<i>нет в наличии</i>"

            item_details = (
                f"📦 <b>{product.title}</b>\n"
                f"💰 Цена: {price_val}\n"
                f"🔗 <a href='{product.url}'>Перейти на WB</a>"
            )

            # Отправляем товары отдельными сообщениями
            bot.send_message(
                message.chat.id,
                item_details,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=get_delete_keyboard(product.id)
            )

    except Exception as e:
        logger.error(f"Ошибка в show_my_products для пользователя {message.from_user.id}: {e}", exc_info=True)
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка при загрузке вашего списка.")

    finally:
        session.close()