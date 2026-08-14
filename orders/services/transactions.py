from django.db import transaction

from ..models import TransactionDetail
from .. import queries

from .marketing import sync_marketing_details
from .pricing import get_area_price


def add_transaction_line(
    customer_detail,
    product,
    order_type,
    quantity,
    invoice_type="",
):
    area_price = get_area_price(
        customer_detail.order.area,
        product,
    )

    line_price = quantity * area_price

    line = TransactionDetail.objects.create(
        customer_detail=customer_detail,
        product=product,
        order_type=order_type,
        invoice_type=invoice_type,
        quantity=quantity,
        line_price=line_price,
    )

    sync_marketing_details(customer_detail.order)

    return line


@transaction.atomic
def delete_transaction_line(line, order):
    line.delete()
    sync_marketing_details(order)


def update_transaction_context(
    session,
    order,
    order_type=None,
    invoice_type=None,
    customer_detail_id=None,
):
    order_type_key = (
        f"transaction_order_type_{order.id}"
    )

    invoice_type_key = (
        f"transaction_invoice_type_{order.id}"
    )

    customer_key = (
        f"transaction_customer_{order.id}"
    )

    valid_order_types = dict(
        TransactionDetail.ORDER_TYPE_CHOICES
    )

    # -------------------------------------------------
    # Order type
    # -------------------------------------------------

    if order_type is not None:

        if order_type in valid_order_types:
            session[order_type_key] = order_type

        elif order_type == "":
            session.pop(
                order_type_key,
                None,
            )

    # -------------------------------------------------
    # Invoice type
    # -------------------------------------------------

    if invoice_type is not None:
        session[invoice_type_key] = invoice_type

    # -------------------------------------------------
    # Customer
    # -------------------------------------------------

    if customer_detail_id is not None:

        if customer_detail_id == "":
            session.pop(
                customer_key,
                None,
            )

        else:
            exists = queries.customer_exists_on_order(
                order,
                customer_detail_id,
            )

            if exists:
                session[customer_key] = int(
                    customer_detail_id
                )