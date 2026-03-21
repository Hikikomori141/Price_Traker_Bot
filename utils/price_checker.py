from apscheduler.schedulers.background import BackgroundScheduler
from loader import bot, logger
from database.db_manager import Session, Product, User
from api.parser_wb import get_price_wb
import time


def check_prices() -> None:
    """
    Функция проверки цен.
    Проходит по всем товарам в БД, парсит актуальную цену и уведомляет об изменениях.
    """
    logger.info("Запуск плановой проверки цен...")
    session = Session()
    try:
        # Берем все товары из базы
        products = session.query(Product).all()

        for product in products:
            data = get_price_wb(product.url)

            # Если товар не найден или нет цены
            if not data or not isinstance(data.get('price'), (int, float)):
                continue

            new_price = float(data['price'])
            old_price = product.current_price

            # Если цена изменилась
            if old_price is None or new_price != old_price:

                # Сохраняем историю цен в БД
                product.last_price = old_price
                product.current_price = new_price
                session.commit()

                # Ищем владельца товара
                user = session.query(User).filter_by(id=product.user_id).first()
                if not user:
                    continue

                # Считаем разницу
                if old_price:
                    diff = round(new_price - old_price, 2)
                    percent = abs(round((diff / old_price) * 100, 1))

                    if diff > 0:
                        trend = f"📈 Подорожало на <b>{percent}%</b>"
                    else:
                        trend = f"📉 Подешевело на <b>{percent}%</b>"

                    message = (
                        f"🔔 **Изменение цены!**\n\n"
                        f"📦 [{product.title}]({product.url})\n"
                        f"💰 Новая цена: *{new_price} BYN*\n"
                        f"Старая цена: {old_price if old_price else '—'} BYN\n"
                        f"{trend} ({abs(round(diff, 2))} BYN)"
                    )

                    try:
                        bot.send_message(user.user_id, message, parse_mode="HTML", disable_web_page_preview=True)
                        time.sleep(0.1)
                    except Exception as send_error:
                        logger.warning(f"Не удалось отправить уведомление пользователю {user.user_id}: {send_error}")

    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка в планировщике: {e}", exc_info=True)
    finally:
        session.close()
        logger.info("Проверка цен завершена.")


def run_scheduler():
    """
    Запускает фоновый процесс, который будет запускать check_prices раз в час.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_prices, 'interval', minutes=60)
    scheduler.start()
    logger.info("Планировщик APScheduler успешно запущен.")
