from django.shortcuts import render, get_object_or_404
from . import services
from orders.models import OrderDetails
from django.db.models import Sum, Q


def record_list(request):
    orders = services.search_orders(
        search=request.GET.get("search"),
        sort=request.GET.get("sort", "-beg_date"),
    )

    return render(request, "records/home.html", {
        "orders": orders,
    })


def record_view(request, order_id):
    order = get_object_or_404(
        OrderDetails.objects.select_related(
            "area",
            "agent",
        ).prefetch_related(
            "customers__customer",
            "customers__transactions",
            "deliveries__product",
            "marketing__product",
        ),
        id=order_id,
    )

    reports = order.marketing.all()

    totals = reports.aggregate(
        total_MRET=Sum("total_MRET"),
        total_MLOAD=Sum("total_MLOAD"),
    )

    totals = {key: value or 0 for key, value in totals.items()}

    totals["total_SO_price"] = sum(
        item.total_SO_price for item in reports
    )

    totals["total_SAM_price"] = sum(
        item.total_SAM_price for item in reports
    )

    totals["total_MRET_price"] = sum(
        item.total_MRET_price for item in reports
    )

    totals["total_CRET_price"] = sum(
        item.total_CRET_price for item in reports
    )

    totals["total_MLOAD_price"] = sum(
        item.total_MLOAD_price for item in reports
    )

    totals["total_VBO_price"] = sum(
        item.total_VBO_price for item in reports
    )

    totals["total_bo_price"] = sum(
        item.total_bo_price for item in reports
    )

    totals["net_value"] = (
        totals["total_SO_price"] +
        totals["total_SAM_price"]
    )

    totals["mld_mrt"] = (
        totals["total_MLOAD_price"] -
        totals["total_MRET_price"]
    )

    totals["so"] = (
        totals["net_value"] -
        totals["mld_mrt"]
    )

    
    collection_totals = order.customers.aggregate(
        cash_total=Sum(
            "transactions__line_price",
            filter=Q(transactions__invoice_type="CASH"),
        ),
        charge_total=Sum(
            "transactions__line_price",
            filter=Q(transactions__invoice_type="CHARGE"),
        ),
    )

    totals["cash_total"] = collection_totals["cash_total"] or 0
    totals["charge_total"] = collection_totals["charge_total"] or 0
    totals["collectible_a"] = totals["charge_total"]

    return render(
        request,
        "records/reports/view.html",
        {
            "order": order,
            "reports": reports,
            "totals": totals,
        },
    )