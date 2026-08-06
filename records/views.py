from django.shortcuts import render, get_object_or_404
from . import services
from orders.models import OrderDetails
from django.db.models import Sum


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

    reports = order.marketing.all()

    totals = reports.aggregate(
        total_SO=Sum("total_SO"),
        total_SAM=Sum("total_SAM"),
        total_MRET=Sum("total_MRET"),
        total_MLOAD=Sum("total_MLOAD"),
        total_CRET=Sum("total_CRET"),
        total_VBO=Sum("total_VBO"),
        total_CBO=Sum("total_CBO"),
    )

    totals = {key: value or 0 for key, value in totals.items()}

    totals["total_out"] = totals["total_SO"] + totals["total_SAM"]
    totals["total_total"] = totals["total_out"] + totals["total_MRET"]
    totals["total_cret_balance"] = totals["total_MLOAD"] - totals["total_total"]
    totals["total_bo"] = totals["total_VBO"] - totals["total_CBO"]


    return render(
        request,
        "records/reports/view.html",
        {
            "order": order,
            "reports": reports,
            'totals': totals,
        },
    )