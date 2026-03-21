import logging
from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data.config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Создаем объект логгера
logger = logging.getLogger("PriceTrackerBot")

# Хранилище состояний
storage = StateMemoryStorage()

# Инициализация бота
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN не найден в переменных окружения!")
    exit(1)

bot = TeleBot(token=BOT_TOKEN, state_storage=storage)