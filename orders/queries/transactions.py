from django.db.models import Sum
from decimal import Decimal

from ..models import TransactionDetail
from .customers import get_selected_customer


def transaction_lines(order, customer_id=None):
    qs = (
        TransactionDetail.objects
        .filter(customer_detail__order=order)
        .select_related(
            "customer_detail",
            "customer_detail__customer",
            "product",
        )
        .order_by("-created_at")
    )
    if customer_id:
        qs = qs.filter(customer_detail_id=customer_id)
    return qs


def get_transaction_totals(order, customer_id=None):
    lines = TransactionDetail.objects.filter(
        customer_detail__order=order
    )
    if customer_id:
        lines = lines.filter(customer_detail_id=customer_id)

    by_type = {}

    for code, _ in TransactionDetail.ORDER_TYPE_CHOICES:
        agg = lines.filter(
            order_type=code
        ).aggregate(
            qty=Sum("quantity"),
            price=Sum("line_price"),
        )

        qty = agg["qty"] or 0
        price = agg["price"] or Decimal("0")

        if code in ["CRET", "CBO"]:
            qty *= -1
            price *= Decimal("-1")

        by_type[code] = {
            "qty": qty,
            "price": price,
        }

    total_qty = (
        by_type["SO"]["qty"]
        + by_type["SAM"]["qty"]
    )

    total_price = (
        by_type["SO"]["price"]
        + by_type["SAM"]["price"]
    )

    so_net_qty = by_type["SO"]["qty"] + by_type["CBO"]["qty"]
    so_net_price = by_type["SO"]["price"] + by_type["CBO"]["price"]

    return {
        "qty": total_qty,
        "price": total_price,
        "amount_due": total_price,
        "bo_amount": abs(by_type["CBO"]["price"]),
        "by_type": by_type,
        "so_net_qty": so_net_qty,
        "so_net_price": so_net_price,
    }


def transaction_page_data(order, customer_id=None):
    selected_customer_detail = None

    if customer_id:
        selected_customer_detail = get_selected_customer(
            order,
            customer_id,
        )

    return {
        "lines": transaction_lines(order, customer_id=customer_id),
        "totals": get_transaction_totals(order, customer_id=customer_id),
        "selected_customer_detail": selected_customer_detail,
    }