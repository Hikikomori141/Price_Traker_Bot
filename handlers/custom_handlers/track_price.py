import re
from telebot.types import Message
from loader import bot, logger
from api.parser_wb import get_price_wb
from database.db_manager import Session, User, Product

@bot.message_handler(func=lambda message: message.text and ("http" in message.text))
def catch_and_save_link(message: Message) -> None:
    """
    Основной обработчик ссылок. Проверяет магазин, парсит цену и сохраняет товар в БД.
    """
    # Ищем ссылку внутри текста
    url_match = re.search(r'(https?://\S+)', message.text)

    if not url_match:
        bot.reply_to(message, "❌ Не смог найти ссылку в сообщении.")
        return

    url = url_match.group(1).strip()
    chat_id = message.chat.id
    user_tg_id = message.from_user.id

    # Сразу уведомляем пользователя
    status_msg = bot.send_message(chat_id, "🔍 Принял ссылку! Начинаю парсинг и сохранение...")

    # Проверка магазина
    if "wildberries" not in url.lower():
        bot.edit_message_text(
            "⚠️ Этот магазин пока не поддерживается.\nПришлите ссылку на <b>Wildberries.by</b>.",
            chat_id, status_msg.message_id, parse_mode="HTML"
        )
        return

    # Парсим данные
    data = get_price_wb(url)

    if not data:
        bot.edit_message_text("🚫 Не удалось получить данные о товаре. Проверь ссылку.", chat_id, status_msg.message_id)
        return

    # Сохраняем в базу данных
    session = Session()
    try:
        # Ищем пользователя в БД
        user = session.query(User).filter_by(user_id=user_tg_id).first()
        if not user:
            bot.edit_message_text("❌ Введи /start для регистрации.", chat_id, status_msg.message_id)
            return

        # Проверяем, не добавлен ли уже этот товар этим пользователем
        existing_product = session.query(Product).filter_by(
            url=url,
            user_id=user.id
        ).first()

        if existing_product:
            bot.edit_message_text(
                f"📝 Вы уже отслеживаете товар:\n<b>{data['title']}</b>",
                chat_id, status_msg.message_id, parse_mode="HTML"
            )
            return

        # Создаем новую запись
        new_product = Product(
            url=url,
            title=data['title'],
            current_price=data['price'] if data['price'] != "нет в наличии" else None,
            last_price=data['price'] if data['price'] != "нет в наличии" else None,
            user_id=user.id
        )

        session.add(new_product)
        session.commit()

        # Финальный ответ
        price_text = f"<b>{data['price']} BYN</b>" if data['price'] != "нет в наличии" else "<i>нет в наличии</i>"
        response = (
            f"✅ <b>Товар добавлен в список!</b>\n\n"
            f"📦 <b>{data['title']}</b>\n"
            f"💰 Текущая цена: {price_text}\n\n"
            f"Я пришлю уведомление, если цена изменится."
        )
        bot.edit_message_text(response, chat_id, status_msg.message_id, parse_mode="HTML")

    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при сохранении ссылки (User: {user_tg_id}): {e}", exc_info=True)
        bot.edit_message_text("⚠️ Ошибка при записи в базу данных.", chat_id, status_msg.message_id)
    finally:
        session.close()


@bot.message_handler(func=lambda message: not message.text.startswith('/'), content_types=['text', 'photo', 'sticker', 'video'])
def handle_unknown_messages(message: Message):
    """
        Ловим всё, что не является командой или ссылкой, и выдаем соответствующее сообщение.
    """
    hint_text = (
        "Чтобы начать отслеживать товар, просто отправь мне <b>ссылку</b> на него с Wildberries.by.\n\n"
        "<i>Пример: https://www.wildberries.by/product?card=...</i>\n\n"
        "📋 <b>Команды:</b>\n"
        "▫️ /my_products — список отслеживания\n"
        "▫️ /help — инструкция\n"
        "▫️ /start — перезапустить бота"
    )

    bot.reply_to(message, hint_text, parse_mode="HTML")