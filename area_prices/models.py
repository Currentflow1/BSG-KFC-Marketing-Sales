from django.db import models
from products.models import Product
from decimal import Decimal

class Area(models.Model):
  area_id = models.BigAutoField(primary_key=True)
  area_name = models.CharField(max_length=255)

  class Meta:
    ordering = ['area_name']

  def __str__(self):
    return self.area_name


class AreaPrice(models.Model):
  area_price_id = models.BigAutoField(primary_key=True)
  area_name = models.ForeignKey(Area, on_delete=models.CASCADE)
  product_name = models.ForeignKey(Product, on_delete=models.CASCADE)
  area_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
