from django.apps import AppConfig

class RatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rates'

    def ready(self):
        from . import auto_fetch
        auto_fetch.start_auto_fetch(interval_minutes=60)  # runs every 5 min
