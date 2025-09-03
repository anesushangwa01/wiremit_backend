from apscheduler.schedulers.background import BackgroundScheduler
from apps.rates.services import aggregate_and_store_rates
import threading
import logging

# -------------------------------
# Logger Setup (single logger)
# -------------------------------
logger = logging.getLogger("forex_scheduler")
logger.setLevel(logging.INFO)

# File logging
file_handler = logging.FileHandler("forex_aggregation.log")
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console logging
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# -------------------------------
# Scheduler Duplicate Prevention
# -------------------------------
scheduler_started = False

# -------------------------------
# Threaded Aggregation
# -------------------------------
def run_aggregate_sync():
    def task():
        logger.info("Starting scheduled forex rate aggregation...")
        try:
            result, api_status = aggregate_and_store_rates()
            for api_name, status, message in api_status:
                if status:
                    logger.info(f"{api_name} fetch successful: {message}")
                else:
                    logger.warning(f"{api_name} fetch failed: {message}")

            if result:
                logger.info("Forex rates aggregated and stored successfully.")
            else:
                logger.warning("Aggregation completed but no rates were stored.")
        except Exception as e:
            logger.exception(f"Unexpected error during forex rate aggregation: {e}")

    threading.Thread(target=task, daemon=True).start()

# -------------------------------
# Scheduler Starter
# -------------------------------
def start_scheduler(interval_minutes=1):
    global scheduler_started
    if scheduler_started:
        logger.info("Scheduler already running. Skipping start.")
        return
    scheduler_started = True

    scheduler = BackgroundScheduler(timezone="Africa/Harare")
    try:
        scheduler.add_job(
            run_aggregate_sync,
            "interval",
            minutes=interval_minutes,
            id="fetch_rates",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
        scheduler.start()
        logger.info(f"APScheduler started, running every {interval_minutes} minutes")
    except Exception as e:
        logger.exception(f"Failed to start APScheduler: {e}")
