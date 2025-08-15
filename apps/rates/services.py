# apps/rates/services.py
import requests
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .models import AggregatedRate

CURRENCYFREAKS_URL = "https://api.currencyfreaks.com/v2.0/rates/latest"
FASTFOREX_URL = "https://api.fastforex.io/fetch-all"
APILAYER_URL = "https://api.apilayer.com/exchangerates_data/latest"


def fetch_rates_from_currencyfreaks():
    try:
        r = requests.get(
            CURRENCYFREAKS_URL,
            params={"apikey": settings.CURRENCYFREAKS_KEY, "symbols": "USD,GBP,ZAR"}
        )
        data = r.json()
        if "rates" not in data:
            raise ValueError(f"No 'rates' key. Full response: {data}")
        print("CurrencyFreaks fetch successful")
        return {"USD": Decimal(data["rates"]["USD"]),
                "GBP": Decimal(data["rates"]["GBP"]),
                "ZAR": Decimal(data["rates"]["ZAR"])}, True
    except Exception as e:
        print("CurrencyFreaks fetch error:", e)
        return None, False


def fetch_rates_from_fastforex():
    try:
        r = requests.get(FASTFOREX_URL, params={"api_key": settings.FASTFOREX_KEY})
        data = r.json().get("results")
        if not data:
            raise ValueError(f"No 'results' key. Full response: {r.json()}")
        print("FastForex fetch successful")
        return {"USD": Decimal(data["USD"]),
                "GBP": Decimal(data["GBP"]),
                "ZAR": Decimal(data["ZAR"])}, True
    except Exception as e:
        print("FastForex fetch error:", e)
        return None, False


def fetch_rates_from_apilayer():
    try:
        headers = {"apikey": settings.APILAYER_KEY}
        r = requests.get(APILAYER_URL, params={"symbols": "USD,GBP,ZAR", "base": "USD"}, headers=headers)
        data = r.json().get("rates")
        if not data:
            raise ValueError(f"No 'rates' key. Full response: {r.json()}")
        print("API Layer fetch successful")
        return {"USD": Decimal("1.0"),
                "GBP": Decimal(data["GBP"]),
                "ZAR": Decimal(data["ZAR"])}, True
    except Exception as e:
        print("API Layer fetch error:", e)
        return None, False


def aggregate_and_store_rates():
    try:
        api_results = [
            ("CurrencyFreaks", fetch_rates_from_currencyfreaks()),
            ("FastForex", fetch_rates_from_fastforex()),
            ("API Layer", fetch_rates_from_apilayer())
        ]

        success_apis = []
        failed_apis = []

        rates_list = []
        for api_name, (data, success) in api_results:
            if success and data:
                success_apis.append(api_name)
                rates_list.append(data)
            else:
                failed_apis.append(api_name)

        if not rates_list:
            print("No valid rates fetched from any API")
            return False

        pairs = [("USD", "GBP"), ("USD", "ZAR"), ("ZAR", "GBP")]

        for base, target in pairs:
            pair_rates = [rate_dict[target] / rate_dict[base] for rate_dict in rates_list]
            avg_rate = sum(pair_rates) / Decimal(len(pair_rates))
            markup_rate = avg_rate * (Decimal("1.0") + Decimal(str(settings.MARKUP_RATE)))

            AggregatedRate.objects.create(
                base_currency=base,
                target_currency=target,
                average_rate=avg_rate,
                markup_rate=markup_rate,
                fetched_at=timezone.now()
            )

        print(f"Forex rates aggregated and stored successfully.")
        print(f"APIs fetched successfully: {', '.join(success_apis) if success_apis else 'None'}")
        print(f"APIs failed: {', '.join(failed_apis) if failed_apis else 'None'}")
        return True

    except Exception as e:
        print("Error aggregating rates:", e)
        return False
