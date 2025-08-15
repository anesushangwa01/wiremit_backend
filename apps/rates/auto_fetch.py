import threading
import time
from django.utils import timezone
from apps.rates.services import aggregate_and_store_rates

def start_auto_fetch(interval_minutes=5):
    """Start a background thread that fetches forex rates automatically."""
    def fetch_loop():
        while True:
            try:
                now = timezone.now()
                print(f"[{now}] Running automatic forex rate fetch...")
                success = aggregate_and_store_rates()
                if success:
                    print(f"[{now}] Forex rates fetched and stored successfully.")
                else:
                    print(f"[{now}] Failed to fetch forex rates.")
            except Exception as e:
                print(f"[{timezone.now()}] Error fetching rates: {e}")
            time.sleep(interval_minutes * 60)  # wait before next fetch

    thread = threading.Thread(target=fetch_loop, daemon=True)
    thread.start()
    print(f"[{timezone.now()}] Auto-fetch thread started, interval = {interval_minutes} minutes")
