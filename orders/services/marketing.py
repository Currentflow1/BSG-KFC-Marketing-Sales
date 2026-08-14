from django.db import transaction

from django.db.models import Sum
from ..models import (
  DeliveryDetail,
  TransactionDetail,
  MarketingDetails,
)


@transaction.atomic
def sync_marketing_details(order):
    product_ids = set(
        DeliveryDetail.objects
        .filter(order=order)
        .values_list("product_id", flat=True)
    ) | set(
        TransactionDetail.objects
        .filter(customer_detail__order=order)
        .values_list("product_id", flat=True)
    )

    for product_id in product_ids:
        MarketingDetails.objects.update_or_create(
            order=order,
            product_id=product_id,
            defaults={

                "total_SO":
                    TransactionDetail.objects.filter(
                        customer_detail__order=order,
                        product_id=product_id,
                        order_type="SO",
                    )
                    .aggregate(total=Sum("quantity"))["total"] or 0,

                "total_SAM":
                    TransactionDetail.objects.filter(
                        customer_detail__order=order,
                        product_id=product_id,
                        order_type="SAM",
                    )
                    .aggregate(total=Sum("quantity"))["total"] or 0,

                "total_CRET":
                    -(
                        TransactionDetail.objects.filter(
                            customer_detail__order=order,
                            product_id=product_id,
                            order_type="CRET",
                        )
                        .aggregate(total=Sum("quantity"))["total"] or 0
                    ),

                "total_CBO":
                    -(
                        TransactionDetail.objects.filter(
                            customer_detail__order=order,
                            product_id=product_id,
                            order_type="CBO",
                        )
                        .aggregate(total=Sum("quantity"))["total"] or 0
                    ),

                "total_MLOAD":
                    DeliveryDetail.objects.filter(
                        order=order,
                        product_id=product_id,
                        order_type="MLOAD",
                    )
                    .aggregate(total=Sum("quantity"))["total"] or 0,

                "total_MRET":
                    -(
                        DeliveryDetail.objects.filter(
                            order=order,
                            product_id=product_id,
                            order_type="MRET",
                        )
                        .aggregate(total=Sum("quantity"))["total"] or 0
                    ),

                "total_VBO":
                    -(
                        DeliveryDetail.objects.filter(
                            order=order,
                            product_id=product_id,
                            order_type="VBO",
                        )
                        .aggregate(total=Sum("quantity"))["total"] or 0
                    ),
            }
        )
