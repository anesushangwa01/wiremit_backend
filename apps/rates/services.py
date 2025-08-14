import os
import requests
from decimal import Decimal, ROUND_HALF_UP
from django.utils.timezone import now
from .models import AggregatedRate

FRANKFURTER_URL = "https://api.frankfurter.app/latest"
CURRENCYFREAKS_URL = "https://api.currencyfreaks.com/latest"
EXCHANGERATEAPI_URL = "https://v6.exchangerate-api.com/v6"

CURRENCYFREAKS_KEY = os.getenv("CURRENCYFREAKS_KEY")
EXCHANGERATEAPI_KEY = os.getenv("EXCHANGERATEAPI_KEY")
MARKUP_RATE = Decimal(str(os.getenv("MARKUP_RATE", 0.10)))

BASE_CURRENCIES = ["USD", "GBP", "ZAR"]

def fetch_frankfurter(base, target):
    try:
        res = requests.get(f"{FRANKFURTER_URL}?from={base}&to={target}", timeout=5)
        res.raise_for_status()
        return Decimal(str(res.json()["rates"][target]))
    except:
        return None

def fetch_currencyfreaks(base, target):
    try:
        res = requests.get(
            f"{CURRENCYFREAKS_URL}?apikey={CURRENCYFREAKS_KEY}&base={base}&symbols={target}",
            timeout=5
        )
        res.raise_for_status()
        return Decimal(str(res.json()["rates"][target]))
    except:
        return None

def fetch_exchangerateapi(base, target):
    try:
        res = requests.get(
            f"{EXCHANGERATEAPI_URL}/{EXCHANGERATEAPI_KEY}/latest/{base}",
            timeout=5
        )
        res.raise_for_status()
        return Decimal(str(res.json()["conversion_rates"][target]))
    except:
        return None

def fetch_all_rates():
    # Define all currency pairs (USD->GBP, USD->ZAR, ZAR->GBP)
    pairs = [
        ("USD", "GBP"),
        ("USD", "ZAR"),
        ("ZAR", "GBP")
    ]

    for base, target in pairs:
        rates = []

        for fetcher in (fetch_frankfurter, fetch_currencyfreaks, fetch_exchangerateapi):
            rate = fetcher(base, target)
            if rate:
                rates.append(rate)

        if rates:
            avg_rate = (sum(rates) / len(rates)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
            markup_rate = (avg_rate + MARKUP_RATE).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

            AggregatedRate.objects.create(
                base_currency=base,
                target_currency=target,
                average_rate=avg_rate,
                markup_rate=markup_rate,
                fetched_at=now()
            )

            print(f"Saved: {base}->{target} Avg={avg_rate} Markup={markup_rate}")
        else:
            print(f"No rates fetched for {base}->{target}")
