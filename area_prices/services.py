from django.db.models import Q

from .models import Area
from .models import AreaPrice


def search_areas(search=None):
    areas = Area.objects.all()

    if search:
        areas = areas.filter(
            area_name__icontains=search
        )

    return areas.order_by("area_name")


def search_area_prices(search=None):
    area_prices = (
        AreaPrice.objects
        .select_related(
            "area_name",
            "product_name",
        )
    )

    if search:
        area_prices = area_prices.filter(
            Q(area_name__area_name__icontains=search)| 
            Q(product_name__product_code__icontains=search)| 
            Q(product_name__product_name__icontains=search)| 
            Q(area_price__icontains=search)
        ).distinct()

    return area_prices