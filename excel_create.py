from datetime import datetime
import pandas as pd


def create_report_excel(alerts, shop_name):

    rows = []

    report_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    for alert in alerts:

        difference = round(
            alert["current_price"] - alert["base_price"],
            2
        )

        percent_difference = round(
            difference / alert["base_price"] * 100,
            2
        )

        rows.append({
            "Тип нарушения":
                "Низкая цена"
                if alert["alert_type"] == "low"
                else "Высокая цена",

            "Артикул": alert["article"],
            "Товар": alert["product_name"],
            "Текущая цена": alert["current_price"],
            "РРЦ": alert["base_price"],
            "Разница, ₽": difference,
            "Отклонение, %": percent_difference,
            "Нижний порог": alert["min_allowed_price"],
            "Верхний порог": alert["max_allowed_price"],
            "Настройка допуска":
                f"-{alert['percent_down']}% / +{alert['percent_up']}%"
        })

    df = pd.DataFrame(rows)

    filename = f"report_{shop_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    shop_name = f"Магазин: {shop_name}"

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:

        # пишем таблицу со сдвигом вниз (строка 4)
        df.to_excel(
            writer,
            index=False,
            sheet_name="Нарушения",
            startrow=3
        )

        ws = writer.sheets["Нарушения"]

        # =========================
        # 🔥 ЗАГОЛОВОК ОТЧЕТА
        # =========================

        title = f"{shop_name} | Отчет от {report_time}"

        ws.merge_cells("A1:K1")
        ws["A1"] = title

        ws["A1"].style = "Title"

        # =========================
        # 📊 ШИРИНЫ КОЛОНОК
        # =========================

        widths = {
            "A": 18,
            "B": 15,
            "C": 50,
            "D": 18,
            "E": 18,
            "F": 15,
            "G": 15,
            "H": 15,
            "I": 15,
            "J": 20,
            "K": 22
        }

        for col, width in widths.items():
            ws.column_dimensions[col].width = width

    return filename