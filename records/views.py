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

    context = {"orders": orders}

    if request.headers.get("HX-Request") == "true":
        return render(request, "records/components/list.html", context)

    return render(request, "records/home.html", context)


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

    totals["total_BO"] = sum(
        item.total_bo for item in reports
    )

    totals["total_CBO_price"] = sum(
        item.total_CBO_price for item in reports
    )

    totals["net_qty"] = sum(item.net_qty for item in reports)
    totals["net_price"] = sum(item.net_price for item in reports)

    totals["total_BO_percentage"] = sum(
            item.total_BO_percentage for item in reports
        )

    totals["total_VBO_display"] = sum(
            item.total_VBO_display for item in reports
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

    return render(request, "records/reports/view.html", {
        "order": order,
        "reports": reports,
        "totals": totals,
    })


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
    totals["total_CBO_price"] = sum(item.total_CBO_price for item in reports)
    totals["net_qty"] = sum(item.net_qty for item in reports)
    totals["net_price"] = sum(item.net_price for item in reports)
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
            marketing.net_qty,
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
    writer.writerow(["SO Price Total", totals["net_price"]])
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


# ============================================================
# Short/Over + MRET % report filtering (shared)
# ============================================================

def _report_filter_options():
    """Dropdown choices shared by the short/over and MRET % report filters."""
    areas = (
        OrderDetails.objects
        .exclude(area__isnull=True)
        .values_list("area_id", "area__area_name")
        .distinct()
        .order_by("area__area_name")
    )
    employees = (
        OrderDetails.objects
        .exclude(agent__isnull=True)
        .values_list("agent_id", "agent__employee_name")
        .distinct()
        .order_by("agent__employee_name")
    )
    products = Product.objects.all().order_by("product_name")
    return areas, employees, products


def _short_over_filtered_queryset(request):
    """
    Shared filtering logic for the short/over and MRET % matrices (screen + CSV):
    date range, product, area, employee (agent) — selected by ID via dropdowns.
    Returns (marketing_qs, products, filters_dict).
    """
    start_date = parse_date(request.GET["start_date"]) if request.GET.get("start_date") else None
    end_date = parse_date(request.GET["end_date"]) if request.GET.get("end_date") else None
    product_id = request.GET.get("product") or None
    area_id = request.GET.get("area") or None
    employee_id = request.GET.get("employee") or None

    orders = OrderDetails.objects.filter(mret_date__isnull=False)
    if start_date:
        orders = orders.filter(mret_date__gte=start_date)
    if end_date:
        orders = orders.filter(mret_date__lte=end_date)
    if area_id:
        orders = orders.filter(area_id=area_id)
    if employee_id:
        orders = orders.filter(agent_id=employee_id)

    marketing_qs = (
        MarketingDetails.objects
        .filter(order__in=orders)
        .select_related("order", "product")
    )
    if product_id:
        marketing_qs = marketing_qs.filter(product_id=product_id)

    area_choices, employee_choices, product_choices = _report_filter_options()

    products = product_choices
    if product_id:
        products = products.filter(pk=product_id)

    selected_product = product_choices.filter(pk=product_id).first() if product_id else None
    area_lookup = dict(area_choices)
    employee_lookup = dict(employee_choices)

    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "product_id": product_id,
        "area_id": area_id,
        "employee_id": employee_id,
        "selected_product_name": selected_product.product_name if selected_product else None,
        "selected_area_name": area_lookup.get(int(area_id)) if area_id else None,
        "selected_employee_name": employee_lookup.get(int(employee_id)) if employee_id else None,
        "area_choices": area_choices,
        "employee_choices": employee_choices,
        "product_choices": product_choices,
    }

    return marketing_qs, products, filters


def _base_matrix_context(filters):
    """Context keys shared by both matrix screen views (filter state + dropdown choices)."""
    return {
        "start_date": filters["start_date"] or "",
        "end_date": filters["end_date"] or "",
        "product_id": filters["product_id"],
        "area_id": filters["area_id"],
        "employee_id": filters["employee_id"],
        "selected_product_name": filters["selected_product_name"],
        "selected_area_name": filters["selected_area_name"],
        "selected_employee_name": filters["selected_employee_name"],
        "area_choices": filters["area_choices"],
        "employee_choices": filters["employee_choices"],
        "product_choices": filters["product_choices"],
    }


def _csv_filename_suffix(filters):
    bits = []
    if filters["start_date"]:
        bits.append(str(filters["start_date"]))
    if filters["end_date"]:
        bits.append(str(filters["end_date"]))
    return f"_{'_to_'.join(bits)}" if bits else ""


def _write_csv_filter_header(writer, title, filters):
    writer.writerow([title])
    if filters["start_date"] or filters["end_date"]:
        writer.writerow(["From", filters["start_date"] or "", "To", filters["end_date"] or ""])
    if filters["selected_area_name"]:
        writer.writerow(["Area", filters["selected_area_name"]])
    if filters["selected_employee_name"]:
        writer.writerow(["Employee", filters["selected_employee_name"]])
    if filters["selected_product_name"]:
        writer.writerow(["Product", filters["selected_product_name"]])
    writer.writerow([])


# ============================================================
# Short/Over matrix
# ============================================================

def short_over_matrix(request):
    """
    Product x Date matrix of Short/Over balances.
    Only includes orders with a completed MRET (mret_date set),
    filtered to mret_date within the selected range, and optionally
    by product, area, and employee (agent) — selected via dropdowns.
    """
    marketing_qs, products, filters = _short_over_filtered_queryset(request)

    matrix = defaultdict(lambda: defaultdict(int))
    date_columns = set()

    for md in marketing_qs:
        d = md.order.mret_date
        date_columns.add(d)
        matrix[md.product.pk][d] += md.total_short_over_balance

    date_columns = sorted(date_columns)

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
        **_base_matrix_context(filters),
    })


def export_short_over_matrix_csv(request):
    """
    CSV export of the Product x Date Short/Over matrix.
    Same filtering logic as short_over_matrix.
    """
    marketing_qs, products, filters = _short_over_filtered_queryset(request)

    matrix = defaultdict(lambda: defaultdict(int))
    date_columns = set()

    for md in marketing_qs:
        d = md.order.mret_date
        date_columns.add(d)
        matrix[md.product.pk][d] += md.total_short_over_balance

    date_columns = sorted(date_columns)

    response = HttpResponse(content_type="text/csv")
    suffix = _csv_filename_suffix(filters)
    response["Content-Disposition"] = (
        f'attachment; filename="short_over_matrix{suffix}.csv"'
    )

    writer = csv.writer(response)
    _write_csv_filter_header(writer, "Short / Over Report — Post-MRET", filters)

    header = ["Product Name"] + [d.strftime("%Y-%m-%d") for d in date_columns]
    writer.writerow(header)

    for product in products:
        row = [product.product_name] + [
            matrix[product.pk].get(d, 0) for d in date_columns
        ]
        writer.writerow(row)

    return response


# ============================================================
# MRET % matrix
# ============================================================

def _mret_pct(cell):
    """
    MRET % = total_MRET / total_MLOAD * 100.
    total_MRET is stored as a negative value (see total_MRET_display
    elsewhere), so it must be negated before use.
    MRET values can never be negative, so the result is floored at 0.
    """
    if not cell["mload"]:
        return 0
    mret = -cell["mret"]  # stored negative; flip sign to get the real magnitude
    return max(0, round((mret / cell["mload"]) * 100, 2))


def mret_percentage_matrix(request):
    """
    Product x Date matrix of MRET % (total_MRET / total_MLOAD * 100).
    Same filtering as short_over_matrix: date range, product, area, employee.
    """
    marketing_qs, products, filters = _short_over_filtered_queryset(request)

    # matrix[product_pk][date] -> {"mret": total, "mload": total}
    matrix = defaultdict(lambda: defaultdict(lambda: {"mret": 0, "mload": 0}))
    date_columns = set()

    for md in marketing_qs:
        d = md.order.mret_date
        date_columns.add(d)
        cell = matrix[md.product.pk][d]
        cell["mret"] += md.total_MRET
        cell["mload"] += md.total_MLOAD

    date_columns = sorted(date_columns)

    rows = [
        {
            "product": product,
            "values": [
                _mret_pct(matrix[product.pk].get(d, {"mret": 0, "mload": 0}))
                for d in date_columns
            ],
        }
        for product in products
    ]

    return render(request, "records/mret_percentage_matrix/mret_percentage_matrix.html", {
        "date_columns": date_columns,
        "rows": rows,
        **_base_matrix_context(filters),
    })


def export_mret_percentage_matrix_csv(request):
    """
    CSV export of the Product x Date MRET % matrix.
    Same filtering logic as mret_percentage_matrix.
    """
    marketing_qs, products, filters = _short_over_filtered_queryset(request)

    matrix = defaultdict(lambda: defaultdict(lambda: {"mret": 0, "mload": 0}))
    date_columns = set()

    for md in marketing_qs:
        d = md.order.mret_date
        date_columns.add(d)
        cell = matrix[md.product.pk][d]
        cell["mret"] += md.total_MRET
        cell["mload"] += md.total_MLOAD

    date_columns = sorted(date_columns)

    response = HttpResponse(content_type="text/csv")
    suffix = _csv_filename_suffix(filters)
    response["Content-Disposition"] = (
        f'attachment; filename="mret_percentage_matrix{suffix}.csv"'
    )

    writer = csv.writer(response)
    _write_csv_filter_header(writer, "MRET % Report — Post-MRET", filters)

    header = ["Product Name"] + [d.strftime("%Y-%m-%d") for d in date_columns]
    writer.writerow(header)

    for product in products:
        row = [product.product_name] + [
            _mret_pct(matrix[product.pk].get(d, {"mret": 0, "mload": 0}))
            for d in date_columns
        ]
        writer.writerow(row)

    return response