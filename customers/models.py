from django.db import models
from area_prices.models import Area

class Customer(models.Model):
  customer_id = models.BigAutoField(primary_key=True)
  customer_area = models.ForeignKey(Area, on_delete=models.CASCADE)
  customer_business_name = models.CharField(max_length=255, default='')
  customer_contact_person = models.CharField(max_length=255, default='')
  customer_mobile_no = models.CharField(max_length=15, default='')
  customer_business_address = models.CharField(max_length=255, default='')
  customer_active = models.BooleanField(default=True)

  class Meta:
    ordering = ['customer_business_name']

  def __str__(self):
    return self.customer_business_name

