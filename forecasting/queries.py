from django.db.models import Case, F, IntegerField, Sum, When
from orders.models import TransactionDetail


class SalesQuery:

    @staticmethod
    def product_daily_history(product_id, start_date=None, end_date=None):

        queryset = (
            TransactionDetail.objects
            .filter(
                product_id=product_id,
                customer_detail__order__beg_date__isnull=False,
            )
            .select_related(
                "customer_detail__order",
                "product",
            )
        )

        if start_date:
            queryset = queryset.filter(
                customer_detail__order__beg_date__gte=start_date
            )

        if end_date:
            queryset = queryset.filter(
                customer_detail__order__beg_date__lte=end_date
            )

        return (
            queryset
            .annotate(
                sales_date=F(
                    "customer_detail__order__beg_date"
                ),

                # NET demand = SO + SAM - CBO (CRET intentionally excluded,
                # matching the SO-minus-CBO rule used elsewhere).
                demand_qty=Case(
                    When(
                        order_type__in=["SO", "SAM"],
                        then=F("quantity"),
                    ),
                    When(
                        order_type="CBO",
                        then=-F("quantity"),
                    ),
                    default=0,
                    output_field=IntegerField(),
                ),

                # Kept as separate diagnostic fields for the summary
                # panel (customer_returns / customer_bad_orders) —
                # NOT re-subtracted from demand a second time.
                return_qty=Case(
                    When(
                        order_type="CRET",
                        then=F("quantity"),
                    ),
                    default=0,
                    output_field=IntegerField(),
                ),

                bad_order_qty=Case(
                    When(
                        order_type="CBO",
                        then=F("quantity"),
                    ),
                    default=0,
                    output_field=IntegerField(),
                ),
            )
            .values("sales_date")
            .annotate(
                demand=Sum("demand_qty"),
                customer_return=Sum("return_qty"),
                customer_bad_order=Sum("bad_order_qty"),
            )
            .order_by("sales_date")
        )


    @staticmethod
    def product_history_count(product_id):
        return (
            TransactionDetail.objects
            .filter(product_id=product_id)
            .count()
        )


    @staticmethod
    def latest_transaction_date(product_id):
        # Must match the same beg_date__isnull=False filter used in
        # product_daily_history. Without it, a product with any
        # transaction on an incomplete order (beg_date=None, since
        # beg_date mirrors mret_date which isn't set until the order
        # is returned) would have this return None on Postgres —
        # NULLs sort FIRST in a descending order there — even though
        # the product has real, valid transaction history. That showed
        # up as a blank "last transaction" alongside otherwise-normal
        # summary numbers.
        return (
            TransactionDetail.objects
            .filter(
                product_id=product_id,
                customer_detail__order__beg_date__isnull=False,
            )
            .order_by(
                "-customer_detail__order__beg_date"
            )
            .values_list(
                "customer_detail__order__beg_date",
                flat=True,
            )
            .first()
        )