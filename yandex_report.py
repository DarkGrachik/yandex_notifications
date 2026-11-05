import requests

#from config2 import API_KEY, BUSINESS_ID


def generate_report(api_key, business_id):

    url = "https://api.partner.market.yandex.ru/v2/reports/goods-prices/generate"

    params = {
        "format": "JSON"
    }

    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }

    body = {
        "businessId": business_id
    }

    response = requests.post(
        url,
        headers=headers,
        params=params,
        json=body
    )

    response.raise_for_status()

    data = response.json()

    report_id = data["result"]["reportId"]

    print("Создан новый отчет:")
    print(report_id)

    return report_id

