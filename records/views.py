import csv
from collections import defaultdict
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from . import services
from orders.models import OrderDetails, MarketingDetails
from products.models import Product
from django.db.models import Sum, Q

def record_list(request):
    orders = services.search_orders(
        search=request.GET.get("search"),
        sort=request.GET.get("sort", "-beg_date"),
    )

    context = {
        "orders": orders,
    }

    if request.headers.get("HX-Request") == "true":
        return render(
            request,
            "records/components/list.html",
            context,
        )

    return render(
        request,
        "records/home.html",
        context,
    )

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

    totals["total_MRET_display"] = totals["total_MRET"] * -1

    totals["total_SO_price"] = sum(item.total_SO_price for item in reports)
    totals["total_SAM_price"] = sum(item.total_SAM_price for item in reports)

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

    totals["total_BO_percentage"] = sum(
            item.total_BO_percentage for item in reports
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

    return response

def short_over_matrix(request):
    """
    Product x Date matrix of Short/Over balances.
    Only includes orders with a completed MRET (mret_date set),
    filtered to mret_date within the selected range.
    """
    start_date = parse_date(request.GET["start_date"]) if request.GET.get("start_date") else None
    end_date = parse_date(request.GET["end_date"]) if request.GET.get("end_date") else None

    orders = OrderDetails.objects.filter(mret_date__isnull=False)
    if start_date:
        orders = orders.filter(mret_date__gte=start_date)
    if end_date:
        orders = orders.filter(mret_date__lte=end_date)

    marketing_qs = (
        MarketingDetails.objects
        .filter(order__in=orders)
        .select_related("order", "product")
    )

    # matrix[product_pk][date] -> summed short/over
    matrix = defaultdict(lambda: defaultdict(int))
    date_columns = set()

    for md in marketing_qs:
        d = md.order.mret_date
        date_columns.add(d)
        matrix[md.product.pk][d] += md.total_short_over_balance

    date_columns = sorted(date_columns)
    products = Product.objects.all().order_by("product_name")

    rows = [
        {
            "product": product,
            "values": [matrix[product.pk].get(d, 0) for d in date_columns],
        }
        for product in products
    ]

    return render(request, "records/short_over_matrix/short_over_matrix.html", {
        "date_columns": date_columns,
        "rows": rows,
        "start_date": request.GET.get("start_date", ""),
        "end_date": request.GET.get("end_date", ""),
    })

def export_short_over_matrix_csv(request):
    """
    CSV export of the Product x Date Short/Over matrix.
    Same filtering logic as short_over_matrix.
    """
    start_date = parse_date(request.GET["start_date"]) if request.GET.get("start_date") else None
    end_date = parse_date(request.GET["end_date"]) if request.GET.get("end_date") else None

    orders = OrderDetails.objects.filter(mret_date__isnull=False)
    if start_date:
        orders = orders.filter(mret_date__gte=start_date)
    if end_date:
        orders = orders.filter(mret_date__lte=end_date)

    marketing_qs = (
        MarketingDetails.objects
        .filter(order__in=orders)
        .select_related("order", "product")
    )

    matrix = defaultdict(lambda: defaultdict(int))
    date_columns = set()

    for md in marketing_qs:
        d = md.order.mret_date
        date_columns.add(d)
        matrix[md.product.pk][d] += md.total_short_over_balance

    date_columns = sorted(date_columns)
    products = Product.objects.all().order_by("product_name")

    response = HttpResponse(content_type="text/csv")
    filename_bits = []
    if start_date:
        filename_bits.append(str(start_date))
    if end_date:
        filename_bits.append(str(end_date))
    suffix = f"_{'_to_'.join(filename_bits)}" if filename_bits else ""
    response["Content-Disposition"] = (
        f'attachment; filename="short_over_matrix{suffix}.csv"'
    )

    writer = csv.writer(response)

    writer.writerow(["Short / Over Report — Post-MRET"])
    if start_date or end_date:
        writer.writerow(["From", start_date or "", "To", end_date or ""])
    writer.writerow([])

    header = ["Product Name"] + [d.strftime("%Y-%m-%d") for d in date_columns]
    writer.writerow(header)

    for product in products:
        row = [product.product_name] + [
            matrix[product.pk].get(d, 0) for d in date_columns
        ]
        writer.writerow(row)

    return response