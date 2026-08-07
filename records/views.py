import csv
from django.http import HttpResponse
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


def export_trip_report_csv(request, order_id):
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

    totals["total_SO_price"] = sum(item.total_SO_price for item in reports)
    totals["total_SAM_price"] = sum(item.total_SAM_price for item in reports)
    totals["total_MRET_price"] = sum(item.total_MRET_price for item in reports)
    totals["total_CRET_price"] = sum(item.total_CRET_price for item in reports)
    totals["total_MLOAD_price"] = sum(item.total_MLOAD_price for item in reports)
    totals["total_VBO_price"] = sum(item.total_VBO_price for item in reports)
    totals["total_bo_price"] = sum(item.total_bo_price for item in reports)

    totals["net_value"] = totals["total_SO_price"] + totals["total_SAM_price"]
    totals["mld_mrt"] = totals["total_MLOAD_price"] - totals["total_MRET_price"]
    totals["so"] = totals["net_value"] - totals["mld_mrt"]

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

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="trip_report_{order.control_no}.csv"'
    )

    writer = csv.writer(response)

    # --- Report header info ---
    writer.writerow(["Trip Sales Report"])
    writer.writerow(["Report No.", order.control_no])
    writer.writerow(["Area", order.area.area_name])
    writer.writerow(["Agent", order.agent.employee_name])
    writer.writerow(["Beginning Date", order.beg_date])
    writer.writerow(["End Date", order.end_date])
    writer.writerow(["MLOAD Date", order.mload_date])
    writer.writerow(["MRET Date", order.mret_date])
    writer.writerow([])

    # --- Trip Sales Inventory (quantity list) ---
    writer.writerow(["Trip Sales Inventory"])
    writer.writerow([
        "Product Name", "SO", "SAM", "OUT", "MRET", "TOTAL",
        "MLOAD", "S/O", "CRET", "VBO", "CBO", "BO",
    ])
    for marketing in reports:
        writer.writerow([
            marketing.product.product_name,
            marketing.total_SO,
            marketing.total_SAM,
            marketing.total_out,
            marketing.total_MRET,
            marketing.total_total,
            marketing.total_MLOAD,
            marketing.total_short_over_balance,
            marketing.total_CRET,
            marketing.total_VBO,
            marketing.total_CBO,
            marketing.total_bo,
        ])
    writer.writerow([
        "TOTAL", "", "", "", totals["total_MRET"], "",
        totals["total_MLOAD"], "", "", "", "", "",
    ])
    writer.writerow([])

    # --- Price / value totals summary ---
    # NOTE: fill in per-row prices here too if record_price_list.html
    # has its own per-product rows (paste that template and I'll add them
    # the same way as the quantity table above).
    writer.writerow(["Price Summary"])
    writer.writerow(["SO Price Total", totals["total_SO_price"]])
    writer.writerow(["SAM Price Total", totals["total_SAM_price"]])
    writer.writerow(["MRET Price Total", totals["total_MRET_price"]])
    writer.writerow(["CRET Price Total", totals["total_CRET_price"]])
    writer.writerow(["MLOAD Price Total", totals["total_MLOAD_price"]])
    writer.writerow(["VBO Price Total", totals["total_VBO_price"]])
    writer.writerow(["BO Price Total", totals["total_bo_price"]])
    writer.writerow(["Net Value", totals["net_value"]])
    writer.writerow(["MLOAD - MRET", totals["mld_mrt"]])
    writer.writerow(["S/O", totals["so"]])
    writer.writerow([])

    # --- Collections summary ---
    writer.writerow(["Collections Summary"])
    writer.writerow(["Cash Total", totals["cash_total"]])
    writer.writerow(["Charge Total", totals["charge_total"]])
    writer.writerow(["Collectible", totals["collectible_a"]])
    writer.writerow([])

    # --- Invoice / Transactions list ---
    writer.writerow(["Invoice List"])
    writer.writerow([
        "Date", "Customer", "Inv Type", "Amount",
        "Inv Bal", "Cash", "Check", "Balance",
    ])
    for customer_detail in order.customers.all():
        for transaction in customer_detail.transactions.all():
            writer.writerow([
                transaction.created_at.strftime("%Y-%m-%d") if transaction.created_at else "",
                str(customer_detail.customer),
                transaction.get_invoice_type_display(),
                transaction.line_price,
                "",  # Inv Bal - manual entry in template, no bound field
                "",  # Cash - manual entry
                "",  # Check - manual entry
                "",  # Balance - manual entry
            ])
    writer.writerow([])

    # --- Denom / Monetary breakdown ---
    # These tables (record_header.html denom grid, and most of the
    # monetary summary grid) are manual-entry cells in the template with
    # no bound Django variables except cash_total/charge_total/
    # collectible_a, which are already exported above in "Collections
    # Summary". Nothing further to export here unless you add real
    # fields/values to those cells in the template.

    return response
