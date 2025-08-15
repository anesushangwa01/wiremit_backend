from django.core.management.base import BaseCommand
from apps.rates.services import aggregate_and_store_rates  # import the actual function

class Command(BaseCommand):
    help = "Fetch and store aggregated forex rates from APIs"

    def handle(self, *args, **kwargs):
        success = aggregate_and_store_rates()  # call it directly
        if success:
            self.stdout.write(self.style.SUCCESS("Forex rates fetched and stored successfully."))
        else:
            self.stdout.write(self.style.ERROR("Failed to fetch forex rates."))
