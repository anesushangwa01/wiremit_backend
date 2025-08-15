from rest_framework import serializers
from .models import AggregatedRate

class AggregatedRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregatedRate
        fields = '__all__'
