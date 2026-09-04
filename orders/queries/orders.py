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

    # control_no is a CharField, so a plain order_by("control_no") sorts
    # lexicographically ("100000" < "99999" as strings) instead of
    # numerically. Once control numbers cross a digit-count boundary
    # (they start at CONTROL_NO_START = 30000 and only increment, see
    # OrderDetails._generate_control_no), a string sort silently puts
    # some older/smaller numbers above newer/bigger ones. Cast to
    # integer for the actual ordering, same approach already used in
    # OrderDetails._generate_control_no.
    sort_field = sort.lstrip("-")
    if sort_field == "control_no":
        descending = sort.startswith("-")
        orders = orders.extra(
            select={"control_no_int": "CAST(control_no AS INTEGER)"}
        ).order_by("-control_no_int" if descending else "control_no_int")
    else:
        orders = orders.order_by(sort)

    return orders


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