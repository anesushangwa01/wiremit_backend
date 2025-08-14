# apps/rates/admin.py
from django.contrib import admin
from .models import AggregatedRate
from .services import fetch_all_rates
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect

@admin.register(AggregatedRate)
class AggregatedRateAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'average_rate', 'markup_rate', 'fetched_at')
    list_filter = ('base_currency', 'target_currency', 'fetched_at')
    search_fields = ('base_currency', 'target_currency')
    ordering = ('-fetched_at',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fetch-latest/', self.admin_site.admin_view(self.fetch_latest_rates), name='fetch_latest_rates'),
        ]
        return custom_urls + urls

    def fetch_latest_rates(self, request):
        """Admin view to fetch latest rates manually."""
        try:
            fetch_all_rates()
            self.message_user(request, "Successfully fetched latest forex rates.")
        except Exception as e:
            self.message_user(request, f"Failed to fetch rates: {str(e)}", level="error")
        return redirect('..')
