from telebot.types import Message
from loader import bot, logger
from database.db_manager import Session, User


@bot.message_handler(commands=['start'])
def handle_start(message: Message) -> None:
    """
    Регистрирует пользователя в базе данных при первом запуске
    и выводит приветственное сообщение с инструкцией.
    """
    session = Session()
    try:
        # Проверяем, есть ли уже такой пользователь в базе
        user = session.query(User).filter_by(user_id=message.from_user.id).first()

        if not user:
            # Создаем новую запись
            new_user = User(
                user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
            session.add(new_user)
            session.commit()
            logger.info(f"Зарегистрирован новый пользователь: {message.from_user.id}")
            greeting = f"👋 <b>Привет, {message.from_user.first_name}!</b> Рад познакомиться.\n\n"
        else:
            greeting = f"👋 <b>С возвращением, {message.from_user.first_name}!</b>\n\n"

        instruction = (
            f"Я — бот для мониторинга цен на <b>Wildberries.by</b>\n\n"
            f"🔍 <b>Что я умею:</b>\n"
            f"1. Следить за ценами на твои любимые товары.\n"
            f"2. Присылать уведомление, если цена упадет или вырастет.\n\n"
            f"📥 <b>Как начать:</b>\n"
            f"Просто отправь мне <b>ссылку</b> на товар с Wildberries.\n\n"
            f"📋 <b>Команды:</b>\n"
            f"/my_products — список отслеживания\n"
            f"/help — инструкция"
        )

        bot.send_message(
            message.chat.id,
            greeting + instruction,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при обработке команды /start для {message.from_user.id}: {e}", exc_info=True)
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка при запуске. Попробуйте чуть позже.")
    finally:
        session.close()
