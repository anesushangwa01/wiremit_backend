from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import AggregatedRate
from .serializers import AggregatedRateSerializer
from .services import fetch_all_rates

# Helper function to fetch recent rates if needed
def ensure_recent_rates():
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_rate = AggregatedRate.objects.filter(fetched_at__gte=one_hour_ago).first()
    if not recent_rate:
        try:
            fetch_all_rates()
        except Exception:
            # Ignore fetching errors; we'll try to return existing data
            pass

# ----------------------------
# /api/rates/?base=&target=
# ----------------------------
@api_view(['GET'])
def list_rates(request):
    ensure_recent_rates()

    queryset = AggregatedRate.objects.all()
    base = request.GET.get('base')
    target = request.GET.get('target')

    if base:
        queryset = queryset.filter(base_currency=base.upper())
    if target:
        queryset = queryset.filter(target_currency=target.upper())

    serializer = AggregatedRateSerializer(queryset, many=True)
    return Response(serializer.data)

# ----------------------------
# /api/rates/{currency}/
# ----------------------------
@api_view(['GET'])
def rates_for_currency(request, currency):
    ensure_recent_rates()

    currency = currency.upper()
    queryset = AggregatedRate.objects.filter(base_currency=currency) | AggregatedRate.objects.filter(target_currency=currency)
    serializer = AggregatedRateSerializer(queryset, many=True)
    return Response(serializer.data)

# ----------------------------
# /api/historical/rates/
# ----------------------------
@api_view(['GET'])
def historical_rates(request):
    # Historical rates can be returned as-is; fetching new is optional
    ensure_recent_rates()

    queryset = AggregatedRate.objects.all().order_by('-fetched_at')
    serializer = AggregatedRateSerializer(queryset, many=True)
    return Response(serializer.data)
