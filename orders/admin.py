from django.contrib import admin
from .models import OrderDetails, DeliveryDetail, CustomerDetails, TransactionDetail
# Register your models here.


admin.site.register(OrderDetails)
admin.site.register(DeliveryDetail)
admin.site.register(CustomerDetails)
admin.site.register(TransactionDetail)
