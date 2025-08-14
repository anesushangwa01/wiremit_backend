# apps/rates/serializers.py
from rest_framework import serializers
from .models import AggregatedRate

class AggregatedRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregatedRate
        fields = ['base_currency', 'target_currency', 'average_rate', 'markup_rate', 'fetched_at']
