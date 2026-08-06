from django.db.models import Case, F, IntegerField, Max, Sum, When

from orders.models import TransactionDetail


class SalesQuery:

    @staticmethod
    def product_daily_history(product_id, start_date=None, end_date=None):
        queryset = (
            TransactionDetail.objects
            .filter(product_id=product_id)
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
                sales_date=F("customer_detail__order__beg_date"),
                signed_quantity=Case(
                    When(
                        order_type__in=["SO", "SAM"],
                        then=F("quantity"),
                    ),
                    When(
                        order_type__in=["CRET", "CBO"],
                        then=-F("quantity"),
                    ),
                    default=0,
                    output_field=IntegerField(),
                ),
            )
            .values("sales_date")
            .annotate(
                demand=Sum("signed_quantity"),
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
        return (
            TransactionDetail.objects
            .filter(product_id=product_id)
            .order_by("-customer_detail__order__beg_date")
            .values_list(
                "customer_detail__order__beg_date",
                flat=True,
            )
            .first()
        )

    @staticmethod
    def total_units_sold(product_id):
        return (
            SalesQuery.product_daily_history(product_id)
            .aggregate(total=Sum("demand"))
            .get("total") or 0
        )

    @staticmethod
    def highest_daily_demand(product_id):
        return (
            SalesQuery.product_daily_history(product_id)
            .aggregate(highest=Max("demand"))
            .get("highest") or 0
        )