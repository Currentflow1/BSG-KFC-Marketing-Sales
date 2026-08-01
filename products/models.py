from django.db import models

class Product(models.Model):
  product_id = models.BigAutoField(primary_key=True)
  product_code = models.CharField(max_length=255, default='')
  product_name = models.CharField(max_length=255, default='')
  factory_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
  shelf_life = models.CharField(max_length=255, default='')
  product_packaging = models.CharField(max_length=255, default='')

  class Meta:
    ordering = ['product_name']

  def __str__(self):
    return self.product_name