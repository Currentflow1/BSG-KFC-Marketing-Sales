from django.db import models

class Product(models.Model):
  product_id = models.BigAutoField(primary_key=True)
  product_code = models.CharField(max_length=255, )
  product_name = models.CharField(max_length=255, )
  factory_price = models.DecimalField(max_digits=10, decimal_places=2)
  shelf_life = models.CharField(max_length=255, )
  product_packaging = models.CharField(max_length=255, )
  discontinued = models.BooleanField(default=False)

  class Meta:
    ordering = ['product_name']

  def __str__(self):
    return self.product_name