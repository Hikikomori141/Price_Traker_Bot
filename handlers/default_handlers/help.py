from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['help'])
def help_command(message: Message) -> None:
    """
    Отправляет пользователю инструкцию по работе с ботом.
    """
    help_text = (
        "❓ <b>Как пользоваться ботом?</b>\n\n"
        "1️⃣ <b>Добавление товара:</b>\n"
        "Просто скопируйте ссылку на товар с сайта Wildberries.by и отправьте её мне сообщением.\n\n"
        "2️⃣ <b>Мониторинг:</b>\n"
        "Я буду проверять цену каждый час. Если она изменится, я сразу пришлю вам уведомление.\n\n"
        "3️⃣ <b>Список товаров:</b>\n"
        "Введите команду /my_products, чтобы увидеть всё, что вы отслеживаете.\n\n"
        "⚠️ <i>Примечание: на данный момент поддерживается только Wildberries.by.</i>"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="HTML")
