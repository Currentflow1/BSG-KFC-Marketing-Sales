from django.db.models import Sum

from decimal import Decimal

from ..models import DeliveryDetail


def delivery_lines(order):
    return (
        DeliveryDetail.objects
        .filter(order=order)
        .select_related("product")
        .order_by("-created_at")
    )

def get_delivery_totals(order):
    lines = DeliveryDetail.objects.filter(order=order)

    by_type = {}

    for code, _ in DeliveryDetail.ORDER_TYPE_CHOICES:
        agg = lines.filter(
            order_type=code
        ).aggregate(
            qty=Sum("quantity"),
            price=Sum("line_price"),
        )

        qty = agg["qty"] or 0
        price = agg["price"] or Decimal("0")

        if code in ["MRET", "VBO"]:
            qty *= -1
            price *= Decimal("-1")

        by_type[code] = {
            "qty": qty,
            "price": price,
        }

    return {
        "qty": sum(x["qty"] for x in by_type.values()),
        "price": sum(x["price"] for x in by_type.values()),
        "by_type": by_type,
    }

def delivery_page_data(order):
    return {
        "lines": delivery_lines(order),
        "totals": get_delivery_totals(order),
    }