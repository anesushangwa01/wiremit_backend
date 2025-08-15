from django.urls import path
from . import views

urlpatterns = [
    path('rates/', views.list_rates, name='list_rates'),  # GET latest aggregated rates
    path('rates/<str:currency>/', views.rates_for_currency, name='rates_for_currency'),
   

    # Historical rates
    path('rates/history/', views.historical_rates_all, name='historical_rates_all'),
  

]
