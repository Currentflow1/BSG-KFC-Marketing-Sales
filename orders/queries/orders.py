from django.db.models import Q

from ..models import OrderDetails


def search_orders(search="", sort="-beg_date"):
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