from django.db import transaction

from ..models import DeliveryDetail
from .marketing import sync_marketing_details
from .pricing import get_area_price


def add_delivery_line(order, product, order_type, quantity):
    area_price = get_area_price(order.area, product)
    line_price = quantity * area_price

    delivery = DeliveryDetail.objects.create(
        order=order,
        product=product,
        order_type=order_type,
        quantity=quantity,
        line_price=line_price,
    )

    sync_marketing_details(order)

    return delivery


@transaction.atomic
def delete_delivery_line(line, order):
    line.delete()
    sync_marketing_details(order)
    

def set_delivery_order_type(session, order, order_type):
    valid_codes = dict(
        DeliveryDetail.ORDER_TYPE_CHOICES
    )

    if order_type not in valid_codes:
        return False

    session[f"delivery_order_type_{order.id}"] = order_type

    return True