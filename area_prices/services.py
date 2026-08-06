from django.db.models import Q
from .models import AreaPrice

def search_area_prices(search=None):
    area_price = AreaPrice.objects.select_related(
        "area_name",
        "product_name"
    )

    if search:
        area_price = area_price.filter(
            Q(area_name__area_name__icontains=search) |          
            Q(product_name__product_code__icontains=search) |   
            Q(product_name__product_name__icontains=search) |  
            Q(area_price__icontains=search)                     
        ).distinct()

    return area_price