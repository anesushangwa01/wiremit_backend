from django.contrib import admin
from .models import AggregatedRate

@admin.register(AggregatedRate)
class AggregatedRateAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'average_rate', 'markup_rate', 'fetched_at')
    list_filter = ('base_currency', 'target_currency')
    search_fields = ('base_currency', 'target_currency')
    ordering = ('-fetched_at',)
