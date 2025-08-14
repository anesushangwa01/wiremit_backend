# apps/rates/services.py
import os
import requests
import logging
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from django.utils.timezone import make_aware, now
from .models import AggregatedRate

logger = logging.getLogger(__name__)

# ----------------------------
# Config
# ----------------------------
CURRENCYFREAKS_KEY = os.getenv("CURRENCYFREAKS_KEY")
FASTFOREX_KEY = os.getenv("FASTFOREX_KEY")
APILAYER_KEY = os.getenv("APILAYER_KEY")
MARKUP_RATE = Decimal(str(os.getenv("MARKUP_RATE", 0.10)))

CURRENCY_PAIRS = [
    ("USD", "GBP"),
    ("USD", "ZAR"),
    ("ZAR", "GBP")
]

# ----------------------------
# Fetch functions for APIs
# ----------------------------
def fetch_currencyfreaks(base, target, date=None):
    """Fetch rate from CurrencyFreaks. Use date='YYYY-MM-DD' for historical."""
    url = "https://api.currencyfreaks.com/v2.0/rates/latest" if not date else "https://api.currencyfreaks.com/v2.0/rates/historical"
    params = {"apikey": CURRENCYFREAKS_KEY}
    if date:
        params["date"] = date
    try:
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
        rate = Decimal(str(res.json()["rates"][target]))
        return rate
    except Exception as e:
        logger.error(f"CurrencyFreaks {('historical ' + date) if date else ''} {base}->{target} error: {e}")
        return None

def fetch_fastforex(base, target, date=None):
    """Fetch rate from FastForex. date='YYYY-MM-DD' for historical."""
    url = "https://api.fastforex.io/fetch-multi" if not date else "https://api.fastforex.io/historical"
    params = {"from": base, "to": target, "api_key": FASTFOREX_KEY}
    if date:
        params["date"] = date
    try:
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
        key = "results" if not date else target
        rate = Decimal(str(res.json()[key][target])) if not date else Decimal(str(res.json()[target]))
        return rate
    except Exception as e:
        logger.error(f"FastForex {('historical ' + date) if date else ''} {base}->{target} error: {e}")
        return None

def fetch_apilayer(base, target, date=None):
    """Fetch rate from APILayer. Use date='YYYY-MM-DD' for historical."""
    url = "https://api.apilayer.com/exchangerates_data/latest" if not date else f"https://api.apilayer.com/exchangerates_data/{date}"
    headers = {"apikey": APILAYER_KEY}
    params = {"base": base, "symbols": target}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        res.raise_for_status()
        rate = Decimal(str(res.json()["rates"][target]))
        return rate
    except Exception as e:
        logger.error(f"APILayer {('historical ' + date) if date else ''} {base}->{target} error: {e}")
        return None

# ----------------------------
# Main fetch function
# ----------------------------
def fetch_all_rates(historical_days=30):
    """
    Fetch and save latest rates + historical rates for the last `historical_days`.
    """
    saved_count = 0
    today = datetime.utcnow().date()

    for delta in range(historical_days, -1, -1):
        fetch_date = today - timedelta(days=delta)
        fetch_date_str = fetch_date.strftime("%Y-%m-%d")

        for base, target in CURRENCY_PAIRS:
            rates = []

            # Fetch rates from all APIs
            for fetcher in (fetch_currencyfreaks, fetch_fastforex, fetch_apilayer):
                rate = fetcher(base, target, date=fetch_date_str if delta != 0 else None)
                if rate:
                    rates.append(rate)

            if rates:
                # Calculate average and markup
                avg_rate = (sum(rates) / len(rates)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
                markup_rate = (avg_rate + MARKUP_RATE).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

                # Determine fetched_at
                fetched_at = make_aware(datetime.combine(fetch_date, datetime.min.time())) if delta != 0 else now()

                # Save to DB (update if exists)
                AggregatedRate.objects.update_or_create(
                    base_currency=base,
                    target_currency=target,
                    fetched_at=fetched_at,
                    defaults={'average_rate': avg_rate, 'markup_rate': markup_rate}
                )
                saved_count += 1
                logger.info(f"Saved {base}->{target} for {fetch_date_str} Avg={avg_rate} Markup={markup_rate}")
            else:
                logger.warning(f"No rates fetched for {base}->{target} on {fetch_date_str}")

    logger.info(f"All rates fetched. Total saved: {saved_count}")
