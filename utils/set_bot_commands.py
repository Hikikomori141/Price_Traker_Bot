from telebot import TeleBot
from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS
from loader import logger


def set_default_commands(bot: TeleBot) -> None:
    """
    Устанавливает список команд бота.
    Данные берутся из DEFAULT_COMMANDS в config.
    """
    try:
        # Преобразуем список в объекты BotCommand
        commands_list = [BotCommand(*i) for i in DEFAULT_COMMANDS]

        # Отправляем запрос в Telegram
        bot.set_my_commands(commands_list)

        logger.info("Команды бота успешно установлены в меню.")

    except Exception as e:
        logger.error(f"Не удалось установить команды бота: {e}", exc_info=True)