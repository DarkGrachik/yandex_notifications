import time
import requests
import zipfile
import io
import json
#from config2 import API_KEY

def wait_report(report_id, api_key):
    url = f"https://api.partner.market.yandex.ru/v2/reports/info/{report_id}"
    headers = {"Api-Key": api_key}

    while True:
        response = requests.get(url, headers=headers)
        data = response.json()

        status = data.get("result", {}).get("status")
        print("Статус:", status)

        if status == "DONE":
            return data["result"]["file"]

        elif status == "FAILED":
            raise Exception("Отчёт не сгенерировался")

        time.sleep(5)


def download_and_parse(file_url):
    print("Скачиваю архив...")

    response = requests.get(file_url)

    zip_file = zipfile.ZipFile(io.BytesIO(response.content))

    print("Файлы в архиве:", zip_file.namelist())

    # берём первый файл (обычно business_prices.json)
    filename = zip_file.namelist()[0]

    with zip_file.open(filename) as f:
        data = json.load(f)

    rows = data.get("rows", [])

    return rows


