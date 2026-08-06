from django.db import models
from products.models import Product

class DailySales(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="daily_sales"
    )
    date = models.DateField()
    quantity = models.PositiveIntegerField()
    revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    class Meta:
        unique_together = ("product", "date")
        ordering = ["date"]


class Forecast(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    forecast_date = models.DateField()
    predicted_quantity = models.FloatField()
    lower_bound = models.FloatField()
    upper_bound = models.FloatField()
    model_name = models.CharField(max_length=50)
    generated_at = models.DateTimeField(auto_now_add=True)
        