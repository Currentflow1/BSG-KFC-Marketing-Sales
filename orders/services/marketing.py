from django.db import transaction
from django.db.models import Q, Sum

from ..models import DeliveryDetail, MarketingDetails, TransactionDetail

MARKETING_FIELDS = [
    "total_SO",
    "total_SAM",
    "total_CRET",
    "total_CBO",
    "total_MLOAD",
    "total_MRET",
    "total_VBO",
]


@transaction.atomic
def sync_marketing_details(order):
    delivery = {
        row["product_id"]: row
        for row in (
            DeliveryDetail.objects.filter(order=order)
            .order_by()
            .values("product_id")
            .annotate(
                MLOAD=Sum("quantity", filter=Q(order_type="MLOAD")),
                MRET=Sum("quantity", filter=Q(order_type="MRET")),
                VBO=Sum("quantity", filter=Q(order_type="VBO")),
            )
        )
    }

    transactions = {
        row["product_id"]: row
        for row in (
            TransactionDetail.objects.filter(customer_detail__order=order)
            .order_by()
            .values("product_id")
            .annotate(
                SO=Sum("quantity", filter=Q(order_type="SO")),
                SAM=Sum("quantity", filter=Q(order_type="SAM")),
                CRET=Sum("quantity", filter=Q(order_type="CRET")),
                CBO=Sum("quantity", filter=Q(order_type="CBO")),
            )
        )
    }

    existing = {
        md.product_id: md
        for md in MarketingDetails.objects.select_for_update().filter(order=order)
    }

    # Include products that already have a marketing row. This is the actual fix:
    # when a product's last line is deleted, it still gets recomputed (to 0).
    product_ids = set(delivery) | set(transactions) | set(existing)

    to_create, to_update = [], []

    for product_id in product_ids:
        d = delivery.get(product_id, {})
        t = transactions.get(product_id, {})

        values = {
            "total_SO": t.get("SO") or 0,
            "total_SAM": t.get("SAM") or 0,
            "total_CRET": -(t.get("CRET") or 0),
            "total_CBO": -(t.get("CBO") or 0),
            "total_MLOAD": d.get("MLOAD") or 0,
            "total_MRET": -(d.get("MRET") or 0),
            "total_VBO": -(d.get("VBO") or 0),
        }

        md = existing.get(product_id)
        if md is None:
            to_create.append(
                MarketingDetails(order=order, product_id=product_id, **values)
            )
        else:
            for field, value in values.items():
                setattr(md, field, value)
            to_update.append(md)

    if to_create:
        MarketingDetails.objects.bulk_create(to_create)
    if to_update:
        MarketingDetails.objects.bulk_update(to_update, MARKETING_FIELDS)