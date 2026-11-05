import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from config2 import PASSWORD

EMAIL = "price@pristavka.com"


def send_email(to_email, alerts, shop_name, attachment_path=None):

    cards_html = ""

    for alert in alerts:

        if alert["alert_type"] == "low":
            title = "Низкая цена"
            description = "Обнаружено снижение цены на товар:"
            limit_name = "Минимальная цена"
            color = "#d93025"
        else:
            title = "Высокая цена"
            description = "Обнаружено превышение цены на товар:"
            limit_name = "Максимальная цена"
            color = "#ea8600"

        cards_html += f"""
        <div style="
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 6px solid {color};
        ">

            <h2 style="color: {color}; margin-top: 0;">
                {title}
            </h2>

            <p style="font-size: 16px;">
                {description}
            </p>

            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Артикул:</td>
                    <td>{alert["article"]}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Товар:</td>
                    <td>{alert["product_name"]}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Текущая цена:</td>
                    <td style="color: green; font-weight: bold;">
                        {alert["current_price"]} ₽
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">{limit_name}:</td>
                    <td>{alert["limit_price"]} ₽</td>
                </tr>
            </table>

        </div>
        """

    html = f"""
    <html>
    <body style="
        font-family: Arial;
        background-color: #f6f8fa;
        padding: 20px;
    ">

        <div style="
            max-width: 700px;
            margin: auto;
        ">

            <div style="
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            ">

                <h1 style="margin: 0;">
                    Мониторинг цен - {shop_name}
                </h1>

                <p style="color: #666;">
                    Найдено отклонений: <b>{len(alerts)}</b>
                </p>

            </div>

            {cards_html}

            <div style="
                background: white;
                padding: 20px;
                border-radius: 10px;
            ">

                <p style="margin: 0; color: #666;">
                    Автоматическое уведомление системы мониторинга цен
                </p>

            </div>

        </div>

    </body>
    </html>
    """

    # ====== СЛУЖЕБНОЕ ИЗМЕНЕНИЕ: multipart ======
    msg = MIMEMultipart()
    msg["Subject"] = f"⚠️ {shop_name}: Обнаружено отклонений цен: {len(alerts)}"
    msg["From"] = EMAIL
    msg["To"] = to_email

    msg.attach(MIMEText(html, "html", "utf-8"))

    # ====== ВЛОЖЕНИЕ ======

    if attachment_path:
        filename = os.path.basename(attachment_path)

        with open(attachment_path, "rb") as f:
            part = MIMEApplication(
                f.read(),
                _subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{filename}"'
        )

        msg.attach(part)

    try:

        server = smtplib.SMTP_SSL("smtp.mail.ru", 465)
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()

        print("Письмо отправлено")
        if attachment_path and os.path.exists(attachment_path):
            os.remove(attachment_path)
            print("Временный файл удалён")

    except Exception as e:

        print("Ошибка отправки письма:", e)