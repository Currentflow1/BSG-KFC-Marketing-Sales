from decimal import Decimal
from django.db.models import Sum, Q
from django.utils import timezone

from area_prices.models import AreaPrice
from .models import OrderDetails, DeliveryDetail, TransactionDetail, CustomerDetails


def get_area_price(area, product):
    """Look up the price for a product in a given area. Raises if not configured."""
    return AreaPrice.objects.get(area_name=area, product_name=product).area_price


def add_delivery_line(order, product, order_type, quantity, remarks=""):
    """Create one MLOAD/MRET/VBO line. Line price is always computed here,
    never trusted from a form field, so it can't drift from area price * qty."""
    area_price = get_area_price(order.area, product)
    line_price = Decimal(quantity) * area_price
    return DeliveryDetail.objects.create(
        order=order,
        product=product,
        order_type=order_type,
        quantity=quantity,
        line_price=line_price,
        remarks=remarks,
    )


def add_transaction_line(customer_detail, product, order_type, quantity, invoice_type="", remarks=""):
    """Create one SO/SAM/CRET/CBO line for a specific customer's invoice."""
    area = customer_detail.order.area
    area_price = get_area_price(area, product)
    line_price = Decimal(quantity) * area_price
    return TransactionDetail.objects.create(
        customer_detail=customer_detail,
        product=product,
        order_type=order_type,
        invoice_type=invoice_type,
        quantity=quantity,
        line_price=line_price,
        remarks=remarks,
    )


def get_delivery_totals(order):
    """Total qty/price for an order's delivery lines, overall and per order_type."""
    lines = DeliveryDetail.objects.filter(order=order)
    overall = lines.aggregate(qty=Sum("quantity"), price=Sum("line_price"))
    by_type = {}
    for code, _ in DeliveryDetail.ORDER_TYPE_CHOICES:
        agg = lines.filter(order_type=code).aggregate(qty=Sum("quantity"), price=Sum("line_price"))
        by_type[code] = {"qty": agg["qty"] or 0, "price": agg["price"] or Decimal("0")}
    return {
        "qty": overall["qty"] or 0,
        "price": overall["price"] or Decimal("0"),
        "by_type": by_type,
    }


def get_transaction_totals(order):
    """Total qty/price for all transaction lines under an order (across all its
    customers/invoices), overall and per order_type. Also computes amount due
    the way an SO/CBO ledger typically wants it: SO+SAM as charges, CRET+CBO as credits."""
    lines = TransactionDetail.objects.filter(customer_detail__order=order)
    overall = lines.aggregate(qty=Sum("quantity"), price=Sum("line_price"))
    by_type = {}
    for code, _ in TransactionDetail.ORDER_TYPE_CHOICES:
        agg = lines.filter(order_type=code).aggregate(qty=Sum("quantity"), price=Sum("line_price"))
        by_type[code] = {"qty": agg["qty"] or 0, "price": agg["price"] or Decimal("0")}

    total_so = by_type["SO"]["price"]
    total_sam = by_type["SAM"]["price"]
    total_cret = by_type["CRET"]["price"]
    total_cbo = by_type["CBO"]["price"]
    bo_amount = total_cbo
    amount_due = (total_so + total_sam) - (total_cret + total_cbo)

    return {
        "qty": overall["qty"] or 0,
        "price": overall["price"] or Decimal("0"),
        "by_type": by_type,
        "bo_amount": bo_amount,
        "amount_due": amount_due,
    }


def get_marketing_summary(order):
    """Fully derived MarketingDetails-equivalent. No stored/cached fields —
    always correct, recomputed on read."""
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


def search_orders(control_no=None, area_id=None, customer_id=None, agent_id=None,
                   product_id=None, van_number=None, sort="-beg_date"):
    qs = OrderDetails.objects.select_related("area", "agent").prefetch_related(
        "customers__customer", "customers__transactions"
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
            Q(deliveries__product_id=product_id) |
            Q(customers__transactions__product_id=product_id)
        ).distinct()
    return qs.order_by(sort)