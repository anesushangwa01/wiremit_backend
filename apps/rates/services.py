import requests
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .models import AggregatedRate
from django.core.cache import cache
import time
import logging

# Use the same logger as auto_fetch.py
logger = logging.getLogger("forex_scheduler")

CURRENCYFREAKS_URL = "https://api.currencyfreaks.com/v2.0/rates/latest"
FASTFOREX_URL = "https://api.fastforex.io/fetch-all"
APILAYER_URL = "https://api.apilayer.com/exchangerates_data/latest"

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def fetch_with_retry(func, *args, **kwargs):
    """Retry wrapper for API calls"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            # Permanent failures: skip retries
            if "no longer active" in str(e) or "exceeded" in str(e):
                raise
            logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}")
        except Exception as e:
            logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}")

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
    raise Exception(f"{func.__name__} failed after {MAX_RETRIES} attempts")


def fetch_rates_from_currencyfreaks():
    r = requests.get(
        CURRENCYFREAKS_URL,
        params={"apikey": settings.CURRENCYFREAKS_KEY, "symbols": "USD,GBP,ZAR"},
        timeout=10
    )
    data = r.json()
    if "rates" not in data:
        raise ValueError(f"No 'rates' key. Full response: {data}")
    return {"USD": Decimal(data["rates"]["USD"]),
            "GBP": Decimal(data["rates"]["GBP"]),
            "ZAR": Decimal(data["rates"]["ZAR"])}


def fetch_rates_from_fastforex():
    r = requests.get(FASTFOREX_URL, params={"api_key": settings.FASTFOREX_KEY}, timeout=10)
    data = r.json().get("results")
    if not data:
        raise ValueError(f"No 'results' key. Full response: {r.json()}")
    return {"USD": Decimal(data["USD"]),
            "GBP": Decimal(data["GBP"]),
            "ZAR": Decimal(data["ZAR"])}


def fetch_rates_from_apilayer():
    headers = {"apikey": settings.APILAYER_KEY}
    r = requests.get(APILAYER_URL, params={"symbols": "USD,GBP,ZAR", "base": "USD"}, headers=headers, timeout=10)
    data = r.json().get("rates")
    if not data:
        raise ValueError(f"No 'rates' key. Full response: {r.json()}")
    return {"USD": Decimal("1.0"),
            "GBP": Decimal(data["GBP"]),
            "ZAR": Decimal(data["ZAR"])}


def aggregate_and_store_rates():
    """
    Fetch rates from all APIs, calculate pair rates, store in DB.
    Returns:
        success (bool), api_status (list of tuples: (API_name, success_bool, message))
    """
    lock_key = "rates_in_progress"
    if not cache.add(lock_key, True, timeout=300):  # 5 min lock
        logger.info("Another worker is already fetching rates. Skipping this run.")
        return False, []

    api_results = []
    api_status = []

    try:
        for api_name, func in [
            ("CurrencyFreaks", fetch_rates_from_currencyfreaks),
            ("FastForex", fetch_rates_from_fastforex),
            ("API Layer", fetch_rates_from_apilayer)
        ]:
            try:
                rates = fetch_with_retry(func)
                api_results.append((api_name, rates))
                api_status.append((api_name, True, "Fetched rates successfully"))
            except Exception as e:
                api_status.append((api_name, False, str(e)))

        if not api_results:
            return False, api_status

        pairs = [("USD", "GBP"), ("USD", "ZAR"), ("ZAR", "GBP")]

        for base, target in pairs:
            pair_rates = []
            for _, rate_dict in api_results:
                try:
                    pair_rates.append(rate_dict[target] / rate_dict[base])
                except Exception as e:
                    logger.warning(f"Error calculating pair {base}->{target} for rates {rate_dict}: {e}")

            if not pair_rates:
                logger.warning(f"No valid pair rates for {base}->{target}. Skipping.")
                continue

            avg_rate = sum(pair_rates) / Decimal(len(pair_rates))
            markup_rate = avg_rate * (Decimal("1.0") + Decimal(str(settings.MARKUP_RATE)))

            try:
                AggregatedRate.objects.create(
                    base_currency=base,
                    target_currency=target,
                    average_rate=avg_rate,
                    markup_rate=markup_rate,
                    fetched_at=timezone.now()
                )
            except Exception as e:
                logger.error(f"Error saving {base}->{target} to DB: {e}")

        return True, api_status

    finally:
        cache.delete(lock_key)
