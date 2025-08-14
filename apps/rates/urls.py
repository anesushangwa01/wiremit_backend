from django.urls import path
from . import views

urlpatterns = [
    # List all latest rates, optional ?base=&target=
    path('rates/', views.list_rates, name='list_rates'),

    # Get all rates for a specific currency
    path('rates/<str:currency>/', views.rates_for_currency, name='rates_for_currency'),

    # Get all historical rates
    path('historical/rates/', views.historical_rates, name='historical_rates'),
]
