from django.db.models import Q

from ..models import OrderDetails

ORDER_SORT_FIELDS = {
    "control_no",
    "beg_date",
    "mload_date",
    "mret_date",
    "area__area_name",
    "agent__employee_name",
}

DEFAULT_SORT = "-control_no"


def _clean_sort(sort):
    field = sort.lstrip("-")
    if field not in ORDER_SORT_FIELDS:
        return DEFAULT_SORT
    return sort

def search_orders(search="", sort="-control_no"):
    sort = _clean_sort(sort)
    orders = (
        OrderDetails.objects
        .select_related("area", "agent")
        .prefetch_related(
            "customers__customer",
            "customers__transactions",
            "deliveries__product",
        )
    )

    if search:
        orders = orders.filter(
            Q(control_no__icontains=search)
            | Q(area__area_name__icontains=search)
            | Q(agent__employee_name__icontains=search)
            | Q(mload_date__icontains=search)
            | Q(mret_date__icontains=search)
            | Q(customers__invoice_no__icontains=search)
            | Q(customers__customer__customer_business_name__icontains=search)
        ).distinct()

    return orders.order_by(sort)


def order_detail_queryset():
    return (
        OrderDetails.objects
        .select_related("area", "agent")
        .prefetch_related(
            "customers__customer",
            "customers__transactions",
            "deliveries__product",
        )
    )