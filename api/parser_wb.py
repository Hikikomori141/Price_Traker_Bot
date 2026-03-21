import requests
import re
from loader import logger


def get_price_wb(url: str) -> dict | None:
    """
    Парсим данные о товаре с Wildberries через их внутреннее API.
    На вход получаем ссылку, на выходе — словарь с названием и ценой.
    """

    # Вытаскиваем только цифры (артикул) из ссылки
    articul_match = re.search(r'(\d+)', url)
    if not articul_match:
        logger.warning(f"Не удалось найти артикул в ссылке: {url}")
        return None

    articul = articul_match.group(1)

    # Используем v4 API, параметры: curr=byn, dest — регион РБ
    api_url = f"https://card.wb.ru/cards/v4/detail?appType=1&curr=byn&dest=-1257786&nm={articul}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }

    try:
        # Таймаут 10 сек, чтобы бот не завис, если WB будет долго отвечать
        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 200:
            json_data = response.json()

            # Проверяем оба варианта расположения списка товаров
            products = json_data.get("products") or json_data.get("data", {}).get("products", [])

            if not products:
                logger.info(f"Товар {articul} не найден")
                return None

            product = products[0]
            title = product.get("name")

            # Пробуем достать цену из разных ключей
            raw_price = product.get("salePriceU") or product.get("product")

            # Если в корне объекта пусто, проверяем в массиве sizes
            if not raw_price:
                sizes = product.get("sizes", [])
                if sizes:
                    price_data = sizes[0].get("price", {})
                    raw_price = price_data.get("total") or price_data.get("product")

            if title and raw_price:
                return {
                    "title": title,
                    "price": float(raw_price) / 100
                }

            elif title:
                return {
                    "title": title,
                    "price": "нет в наличии"
                }

        else:
            logger.error(f"Ошибка API Wildberries: статус {response.status_code}")

    except Exception as e:
        logger.error(f"Критическая ошибка при запросе к WB: {e}", exc_info=True)

    return None


if __name__ == '__main__':
    # Тестовый запуск модуля
    test_url = "https://www.wildberries.by/catalog/17296798/detail.aspx"
    result = get_price_wb(test_url)
    print("Результат теста:", result)
