from django.apps import AppConfig


class RatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rates'

    def ready(self):
        # Import and start scheduler only once
        from django.conf import settings
        if settings.SCHEDULER_AUTOSTART:
            from .auto_fetch import start_scheduler
            start_scheduler()
