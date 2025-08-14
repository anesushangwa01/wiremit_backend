from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Max
from .models import AggregatedRate
from .serializers import AggregatedRateSerializer
from .services import fetch_all_rates
import logging

logger = logging.getLogger(__name__)

# ----------------------------
# Helper: Ensure recent rates exist
# ----------------------------
def ensure_recent_rates():
    """Fetch rates if there are no records in the last hour."""
    one_hour_ago = timezone.now() - timedelta(hours=1)
    if not AggregatedRate.objects.filter(fetched_at__gte=one_hour_ago).exists():
        try:
            fetch_all_rates()
            logger.info("Successfully fetched latest rates.")
        except Exception as e:
            logger.error(f"Error fetching rates: {str(e)}")

# ----------------------------
# /api/rates/?base=&target=
# Returns latest rates per currency pair
# ----------------------------
@api_view(['GET'])
def list_rates(request):
    ensure_recent_rates()

    # Get latest fetched_at per currency pair
    latest_per_pair = (
        AggregatedRate.objects
        .values('base_currency', 'target_currency')
        .annotate(latest_fetched=Max('fetched_at'))
    )

    # Build queryset with only the latest records
    latest_ids = [
        AggregatedRate.objects.filter(
            base_currency=item['base_currency'],
            target_currency=item['target_currency'],
            fetched_at=item['latest_fetched']
        ).values_list('id', flat=True).first()
        for item in latest_per_pair
    ]

    queryset = AggregatedRate.objects.filter(id__in=latest_ids)

    # Optional filtering by base or target
    base = request.GET.get('base')
    target = request.GET.get('target')
    if base:
        queryset = queryset.filter(base_currency=base.upper())
    if target:
        queryset = queryset.filter(target_currency=target.upper())

    if not queryset.exists():
        return Response({"message": "No rates available.", "rates": []})

    serializer = AggregatedRateSerializer(queryset, many=True)
    return Response(serializer.data)

# ----------------------------
# /api/rates/{currency}/
# Returns latest rates where currency is base or target
# ----------------------------
@api_view(['GET'])
def rates_for_currency(request, currency):
    ensure_recent_rates()
    currency = currency.upper()

    queryset = AggregatedRate.objects.filter(base_currency=currency) | AggregatedRate.objects.filter(target_currency=currency)
    queryset = queryset.distinct().order_by('-fetched_at')

    if not queryset.exists():
        return Response({"message": f"No rates available for {currency}.", "rates": []})

    serializer = AggregatedRateSerializer(queryset, many=True)
    return Response(serializer.data)

# ----------------------------
# /api/rates/historical/
# Returns all historical rates from database
# ----------------------------
@api_view(['GET'])
def historical_rates(request):
    # Ensure there is at least some data
    if not AggregatedRate.objects.exists():
        try:
            fetch_all_rates()
            logger.info("Fetched initial rates for historical view.")
        except Exception as e:
            logger.error(f"Error fetching initial rates: {str(e)}")
            return Response({
                "message": "No historical rates available. Fetch attempt failed.",
                "rates": []
            })

    queryset = AggregatedRate.objects.all().order_by('-fetched_at')

    serializer = AggregatedRateSerializer(queryset, many=True)
    return Response(serializer.data)

