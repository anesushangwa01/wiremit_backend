from django.db import models

class AggregatedRate(models.Model):
    base_currency = models.CharField(max_length=3)
    target_currency = models.CharField(max_length=3)
    average_rate = models.DecimalField(max_digits=12, decimal_places=6)
    markup_rate = models.DecimalField(max_digits=12, decimal_places=6)
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.base_currency}->{self.target_currency}: {self.average_rate}"
