from loader import bot, logger
import handlers
from database.db_manager import create_db
from utils.set_bot_commands import set_default_commands
from utils.price_checker import run_scheduler

if __name__ == "__main__":
    try:
        # Инициализация базы данных
        create_db()

        # Установка команд в меню бота
        set_default_commands(bot)

        # Запуск фонового планировщика для проверки цен
        run_scheduler()

        logger.info("Бот запущен...")

        # Запуск polling
        bot.infinity_polling()

    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {e}", exc_info=True)
        exit(1)
