from decimal import Decimal

from django.db.models import Q, Sum
from django.utils import timezone

from area_prices.models import AreaPrice
from .models import (
    OrderDetails,
    DeliveryDetail,
    TransactionDetail,
    MarketingDetails,
)

def get_area_price(area, product):
    return AreaPrice.objects.get(
        area_name=area,
        product_name=product,
    ).area_price


def add_delivery_line(order, product, order_type, quantity, remarks=""):
    area_price = get_area_price(order.area, product)
    line_price = Decimal(quantity) * area_price

    line = DeliveryDetail.objects.create(
        order=order,
        product=product,
        order_type=order_type,
        quantity=quantity,
        line_price=line_price,
        remarks=remarks,
    )

    sync_marketing_details(order)
    return line


def add_transaction_line(
    customer_detail,
    product,
    order_type,
    quantity,
    invoice_type="",
    remarks="",
):
    area_price = get_area_price(customer_detail.order.area, product)
    line_price = Decimal(quantity) * area_price

    line = TransactionDetail.objects.create(
        customer_detail=customer_detail,
        product=product,
        order_type=order_type,
        invoice_type=invoice_type,
        quantity=quantity,
        line_price=line_price,
        remarks=remarks,
    )

    sync_marketing_details(customer_detail.order)
    return line


def get_delivery_totals(order):
    lines = DeliveryDetail.objects.filter(order=order)

    by_type = {}

    for code, _ in DeliveryDetail.ORDER_TYPE_CHOICES:
        agg = lines.filter(order_type=code).aggregate(
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
        "qty": sum(v["qty"] for v in by_type.values()),
        "price": sum(v["price"] for v in by_type.values()),
        "by_type": by_type,
    }


def get_transaction_totals(order):
    lines = TransactionDetail.objects.filter(customer_detail__order=order)

    by_type = {}

    for code, _ in TransactionDetail.ORDER_TYPE_CHOICES:
        agg = lines.filter(order_type=code).aggregate(
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

    total_qty = by_type["SO"]["qty"] + by_type["SAM"]["qty"]
    total_price = by_type["SO"]["price"] + by_type["SAM"]["price"]

    return {
        "qty": total_qty,
        "price": total_price,
        "amount_due": total_price,
        "bo_amount": abs(by_type["CBO"]["price"]),
        "by_type": by_type,
    }


def get_marketing_summary(order):
    delivery = get_delivery_totals(order)
    transaction = get_transaction_totals(order)

    return {
        "total_SO": transaction["by_type"]["SO"]["qty"],
        "total_SAM": transaction["by_type"]["SAM"]["qty"],
        "total_CRET": transaction["by_type"]["CRET"]["qty"],
        "total_CBO": transaction["by_type"]["CBO"]["qty"],
        "total_MLOAD": delivery["by_type"]["MLOAD"]["qty"],
        "total_MRET": delivery["by_type"]["MRET"]["qty"],
        "total_VBO": delivery["by_type"]["VBO"]["qty"],
    }


def complete_order(order):
    order.end_date = timezone.now()
    order.save(update_fields=["end_date"])
    return order


def search_orders(
    control_no=None,
    area_id=None,
    customer_id=None,
    agent_id=None,
    product_id=None,
    van_number=None,
    sort="-beg_date",
):
    qs = OrderDetails.objects.select_related(
        "area",
        "agent",
    ).prefetch_related(
        "customers__customer",
        "customers__transactions",
    )

    if control_no:
        qs = qs.filter(control_no__icontains=control_no)
    if area_id:
        qs = qs.filter(area_id=area_id)
    if agent_id:
        qs = qs.filter(agent_id=agent_id)
    if van_number:
        qs = qs.filter(van_number=van_number)
    if customer_id:
        qs = qs.filter(customers__customer_id=customer_id).distinct()
    if product_id:
        qs = qs.filter(
            Q(deliveries__product_id=product_id)
            | Q(customers__transactions__product_id=product_id)
        ).distinct()

    return qs.order_by(sort)


def sync_marketing_details(order):
    """
    Create/update one MarketingDetails row per product in an order.
    """

    product_ids = set(
        DeliveryDetail.objects.filter(order=order).values_list("product_id", flat=True)
    ) | set(
        TransactionDetail.objects.filter(
            customer_detail__order=order
        ).values_list("product_id", flat=True)
    )

    for product_id in product_ids:
        MarketingDetails.objects.update_or_create(
            order=order,
            product_id=product_id,
            defaults={
                "total_SO": TransactionDetail.objects.filter(
                    customer_detail__order=order,
                    product_id=product_id,
                    order_type="SO",
                ).aggregate(total=Sum("quantity"))["total"] or 0,

                "total_SAM": TransactionDetail.objects.filter(
                    customer_detail__order=order,
                    product_id=product_id,
                    order_type="SAM",
                ).aggregate(total=Sum("quantity"))["total"] or 0,

                "total_CRET": TransactionDetail.objects.filter(
                    customer_detail__order=order,
                    product_id=product_id,
                    order_type="CRET",
                ).aggregate(total=Sum("quantity"))["total"] or 0,

                "total_CBO": TransactionDetail.objects.filter(
                    customer_detail__order=order,
                    product_id=product_id,
                    order_type="CBO",
                ).aggregate(total=Sum("quantity"))["total"] or 0,

                "total_MLOAD": DeliveryDetail.objects.filter(
                    order=order,
                    product_id=product_id,
                    order_type="MLOAD",
                ).aggregate(total=Sum("quantity"))["total"] or 0,

                "total_MRET": DeliveryDetail.objects.filter(
                    order=order,
                    product_id=product_id,
                    order_type="MRET",
                ).aggregate(total=Sum("quantity"))["total"] or 0,

                "total_VBO": DeliveryDetail.objects.filter(
                    order=order,
                    product_id=product_id,
                    order_type="VBO",
                ).aggregate(total=Sum("quantity"))["total"] or 0,
            },
        )