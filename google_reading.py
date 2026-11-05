import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import sys

def resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)


# =========================
# ПОДКЛЮЧЕНИЕ GOOGLE SHEETS
# =========================

CREDS_FILE = resource_path("credentials.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]


def get_spreadsheet(spreadsheet_id):

    creds = Credentials.from_service_account_file(
        CREDS_FILE,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    return client.open_by_key(spreadsheet_id)


# =========================
# ЗАГРУЗКА НАСТРОЕК
# =========================

def load_settings(spreadsheet_id):

    spreadsheet = get_spreadsheet(spreadsheet_id)

    worksheet = spreadsheet.worksheet(
        "Settings"
    )

    settings_df = pd.DataFrame(
        worksheet.get_all_values()
    )

    settings = {}

    for _, row in settings_df.iterrows():

        key = str(row.iloc[0]).strip()
        value = row.iloc[1]

        settings[key] = value

    return {
        "update_minutes": int(
            settings["update_minutes"]
        ),
        "email": settings["email"],
        "percent_down": float(
            settings["percent_down"]
        ),
        "percent_up": float(
            settings["percent_up"]
        )
    }


# =========================
# ЗАГРУЗКА ТОВАРОВ
# =========================

def load_products(spreadsheet_id):

    spreadsheet = get_spreadsheet(spreadsheet_id)

    worksheet = spreadsheet.worksheet(
        "Products"
    )

    records = worksheet.get_all_records()

    products_df = pd.DataFrame(
        records
    )

    products = []

    for _, row in products_df.iterrows():

        article = str(
            row.iloc[0]
        ).strip()

        min_price = float(
            row.iloc[1]
        )

        percent_down = float(row.iloc[2]) if row.iloc[2] != "" else None
        percent_up = float(row.iloc[3]) if row.iloc[3] != "" else None

        products.append({
            "article": article,
            "min_price": min_price,
            "percent_down": percent_down,
            "percent_up": percent_up
        })

    return products