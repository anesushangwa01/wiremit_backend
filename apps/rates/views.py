from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.utils.timezone import localtime
from datetime import datetime, time
from .models import AggregatedRate
from .serializers import AggregatedRateSerializer
from django.utils import timezone


def serialize_rates(rates_queryset):
    """
    Serialize rates and convert fetched_at to Central Africa Time (CAT)
    """
    serialized = AggregatedRateSerializer(rates_queryset, many=True).data
    for item, obj in zip(serialized, rates_queryset):
        item['fetched_at'] = localtime(obj.fetched_at).isoformat()
    return serialized


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_rates(request):
    """
    List all rates (latest first) with count.
    """
    rates = AggregatedRate.objects.all().order_by('-fetched_at')
    serialized = serialize_rates(rates)
    return Response({
        "count": rates.count(),
        "results": serialized
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rates_for_currency(request, currency):
    """
    Rates filtered by currency (as base or target) with count.
    """
    currency = currency.upper()
    rates = AggregatedRate.objects.filter(
        Q(base_currency__iexact=currency) | Q(target_currency__iexact=currency)
    ).order_by('-fetched_at')

    if not rates.exists():
        return Response({"detail": f"No rates found for currency '{currency}'"}, status=404)

    serialized = serialize_rates(rates)
    return Response({
        "count": rates.count(),
        "results": serialized
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest_rates_all(request):
    """
    Latest rates for all currencies with count.
    """
    latest_time = AggregatedRate.objects.order_by('-fetched_at').values_list('fetched_at', flat=True).first()
    if not latest_time:
        return Response({"detail": "No rates found."}, status=404)

    rates = AggregatedRate.objects.filter(fetched_at=latest_time).order_by('base_currency', 'target_currency')
    serialized = serialize_rates(rates)
    return Response({
        "count": rates.count(),
        "results": serialized
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest_rates_currency(request, currency):
    """
    Latest rates for a specific currency (base or target) with count.
    """
    latest_time = AggregatedRate.objects.order_by('-fetched_at').values_list('fetched_at', flat=True).first()
    if not latest_time:
        return Response({"detail": "No rates found."}, status=404)

    currency = currency.upper()
    rates = AggregatedRate.objects.filter(fetched_at=latest_time).filter(base_currency__iexact=currency) | \
            AggregatedRate.objects.filter(fetched_at=latest_time, target_currency__iexact=currency)
    rates = rates.order_by('base_currency', 'target_currency')

    if not rates.exists():
        return Response({"detail": f"No latest rates found for currency '{currency}'"}, status=404)

    serialized = serialize_rates(rates)
    return Response({
        "count": rates.count(),
        "results": serialized
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historical_rates_all(request):
    """
    Historical rates with optional filtering by currency and date, with count.
    Optional query params:
        ?currency=USD
        ?date=YYYY-MM-DD (in CAT)
    """
    currency = request.GET.get('currency', None)
    date_str = request.GET.get('date', None)
    rates = AggregatedRate.objects.all()

    if currency:
        currency = currency.upper()
        rates = rates.filter(Q(base_currency__iexact=currency) | Q(target_currency__iexact=currency))

    if date_str:
        try:
            local_date = datetime.strptime(date_str, "%Y-%m-%d")
            tz = timezone.get_current_timezone()  # should be CAT if TIME_ZONE='Africa/Harare'
            start = timezone.make_aware(datetime.combine(local_date, time.min), tz)
            end = timezone.make_aware(datetime.combine(local_date, time.max), tz)
            rates = rates.filter(fetched_at__range=(start, end))
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    rates = rates.order_by('-fetched_at', 'base_currency', 'target_currency')

    if not rates.exists():
        return Response(
            {"detail": f"No historical rates found for currency '{currency}' on date '{date_str}'"} 
            if currency or date_str else {"detail": "No historical rates found."},
            status=404
        )

    serialized = serialize_rates(rates)
    return Response({
        "count": rates.count(),
        "results": serialized
    })
