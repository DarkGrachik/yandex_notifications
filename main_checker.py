import time
import pandas as pd


#from excel_reading import load_settings, load_products
from google_reading import load_settings, load_products
from yandex_report import generate_report
from yandex_after_report import wait_report, download_and_parse
from notification_mail import send_email
from excel_create import create_report_excel
from shops_config import SHOPS


# =========================
# ЗАГРУЗКА ДАННЫХ
# =========================

# settings = load_settings()
# products = load_products()

# update_minutes = settings["update_minutes"]
# email = settings["email"]

# print("Настройки:")
# print(f"Обновление: {update_minutes} минут")
# print(f"Email: {email}")


# =========================
# JSON -> словарь цен
# =========================

def build_price_map(rows):

    price_map = {}

    for row in rows:

        article = str(row.get("offerId", "")).strip()

        if not article:
            continue

        price_map[article] = {
            "price": row.get("onDisplay"),
            "name": row.get("offerName", "")
        }

    return price_map


# =========================
# ПРОВЕРКА
# =========================

def check_prices(products, price_map, email, default_percent_down, default_percent_up, config):

    print("\nРЕЗУЛЬТАТ ПРОВЕРКИ:\n")

    alerts = []

    for product in products:

        article = product["article"]
        min_price = product["min_price"]

        percent_down = product["percent_down"]
        percent_up = product["percent_up"]

        if pd.isna(percent_down):
            percent_down = default_percent_down

        if pd.isna(percent_up):
            percent_up = default_percent_up

        min_allowed_price = round(min_price * (1 - percent_down / 100), 2)
        max_allowed_price = round(min_price * (1 + percent_up / 100), 2)

        # нет товара
        if article not in price_map:

            print(f"{article} -> нет")
            continue

        item = price_map[article]

        current_price = item["price"]
        product_name = item["name"]

        if current_price is None:

            print(f"{article} -> нет цены")
            continue

        current_price = float(current_price)

        # НИЗКАЯ ЦЕНА
        if current_price < min_allowed_price:

            print(
                f"{article} -> низкая цена "
                f"({current_price} < {min_allowed_price})"
            )

            alerts.append({
                "alert_type": "low",
                "article": article,
                "product_name": product_name,

                "current_price": current_price,

                "base_price": min_price,
                "limit_price": min_allowed_price,

                "min_allowed_price": min_allowed_price,
                "max_allowed_price": max_allowed_price,

                "percent_down": percent_down,
                "percent_up": percent_up
            })

        # ВЫСОКАЯ ЦЕНА
        elif current_price > max_allowed_price:

            print(
                f"{article} -> высокая цена "
                f"({current_price} > {max_allowed_price})"
            )

            alerts.append({
                "alert_type": "high",
                "article": article,
                "product_name": product_name,

                "current_price": current_price,
                "limit_price": max_allowed_price,

                "base_price": min_price,

                "min_allowed_price": min_allowed_price,
                "max_allowed_price": max_allowed_price,

                "percent_down": percent_down,
                "percent_up": percent_up
            })

        # НОРМАЛЬНАЯ ЦЕНА
        else:

            print(
                f"{article} -> нормальная цена "
                f"({min_allowed_price:.2f} <= "
                f"{current_price:.2f} <= "
                f"{max_allowed_price:.2f})"
            )

    # Отправляем одно письмо после завершения проверки

    if alerts:

        excel_file = create_report_excel(alerts,config["name"])

        send_email(
            to_email=email,
            alerts=alerts,
            shop_name = config["name"],
            attachment_path=excel_file
        )

        print(f"\nОтправлено уведомление: {len(alerts)} нарушений")

    else:

        print("\nНарушений не найдено")


def run_shop(shop_name, config):

    print(f"\n======================")
    print(f"Запуск проверки: {shop_name}")
    print(f"======================\n")

    settings = load_settings(config["spreadsheet_id"])
    products = load_products(config["spreadsheet_id"])

    update_minutes = settings["update_minutes"]
    email = settings["email"]

    print(f"Магазин: {shop_name}")
    print(f"Email: {email}")
    print(f"Частота: {update_minutes} мин")

    report_id = generate_report(config["api_key"],config["business_id"])

    file_url = wait_report(report_id, config["api_key"])

    print("Отчёт получен:", file_url)

    rows = download_and_parse(file_url)

    print(f"Товаров в отчёте: {len(rows)}")

    price_map = build_price_map(rows)

    check_prices(
        products,
        price_map,
        email,
        settings["percent_down"],
        settings["percent_up"],
        config
    )

    print(f"\nГотово: {shop_name}\n")

# =========================
# MAIN LOOP
# =========================

import time

def main():

    shops = list(SHOPS.keys())
    last_run = {}

    while True:

        now = time.time()

        for shop in shops:

            try:
                config = SHOPS[shop]
                settings = load_settings(config["spreadsheet_id"])

                update_minutes = settings["update_minutes"]
                interval_sec = update_minutes * 60

                last_time = last_run.get(shop, 0)

                time_since_run = now - last_time
                time_left = interval_sec - time_since_run

                if time_left > 0:
                    print(f"[{shop}] ждём ещё {int(time_left)} сек до запуска")
                    continue

                print(f"[{shop}] запускаем проверку (прошло {int(time_since_run)} сек)")
                

                run_shop(shop, config)

                last_run[shop] = time.time()

            except Exception as e:

                print(f"[{shop}] ошибка проверки:")
                print(e)

        print("\nЦикл проверки завершён. Пауза 60 сек...\n")
        time.sleep(60)

if __name__ == "__main__":
    main()