from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from login.decorators import permission_required_redirect

from . import queries, services
from .forms import (
    CustomerDetailForm,
    DeliveryLineForm,
    OrderForm,
    TransactionLineForm,
)

from .models import (
    CustomerDetails,
    DeliveryDetail,
    OrderDetails,
    TransactionDetail,
)

# ============================================================
# Orders
# ============================================================

@login_required
def order_list(request):
    search = request.GET.get("search", "").strip()
    sort = request.GET.get("sort", "-beg_date")

    orders = queries.search_orders(search=search, sort=sort)

    return render(request, "orders/home.html", {
        "orders": orders,
    })

@login_required
def order_search(request):
    search = request.GET.get("search", "").strip()
    sort = request.GET.get("sort", "-beg_date")

    orders = queries.search_orders(search=search, sort=sort)

    return render(request, "orders/components/main_order/main_order_list.html", {
        "orders": orders,
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(queries.order_detail_queryset(), pk=order_id)

    customer_form = CustomerDetailForm(area=order.area)

    return render(request, "orders/detail.html", {
        "order": order,
        "customer_form": customer_form,
        "marketing_summary": queries.get_marketing_summary(
            order
        ),
        "unpriced_products": queries.get_unpriced_products(
            order.area
        ),
    })

# ============================================================
# Order CRUD
# ============================================================

@permission_required_redirect("orders.add_orderdetails")
def order_new(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()

            messages.success(request, f"Order {order.control_no} created.")
            return redirect("order_list")
    else:
        form = OrderForm()

    return render(request, "orders/new.html", {
        "form": form,
    })


@permission_required_redirect("orders.change_orderdetails")
def order_edit(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()

            messages.success(request, f"Order {order.control_no} updated.")
            return redirect("order_list")
    else:
        form = OrderForm(instance=order)

    return render(request, "orders/edit.html", {
        "form": form,
        "order": order,
    })

@permission_required_redirect("orders.delete_orderdetails")
def order_delete(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id) 
    if request.method == "POST":
        services.delete_order(order)

        messages.success(request, "Order deleted.")
        return redirect("order_list")

    return render(request, "orders/delete.html", {
        "order": order,
    })

@permission_required_redirect("orders.change_orderdetails")
def order_complete(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    if request.method == "POST":
        services.complete_order(order)

        messages.success(request, f"Order {order.control_no} marked complete.")

    return redirect("order_detail", order_id=order.id)

@permission_required_redirect("orders.change_orderdetails")
def order_uncomplete(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)

    if request.method == "POST":
        services.reopen_order(order)

        messages.success(request, f"Order {order.control_no} reopened.")

    return redirect("order_detail", order_id=order.id)

# ============================================================
# Delivery
# ============================================================

@login_required
def manage_delivery(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    session_key = f"delivery_order_type_{order.id}"

    if request.method == "POST":
        form = DeliveryLineForm(request.POST, area=order.area)

        if form.is_valid():
            try:
                services.add_delivery_line(
                    order=order,
                    product=form.cleaned_data["product"],
                    order_type=form.cleaned_data["order_type"],
                    quantity=form.cleaned_data["quantity"],
                )
                messages.success(request, "Delivery line added.")

                return redirect("manage_delivery", order_id=order.id)

            except ValueError as e:
                messages.error(request, str(e))
                form = DeliveryLineForm(area=order.area)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DeliveryLineForm(area=order.area)

    selected_order_type = request.session.get(
        session_key,
        DeliveryDetail.ORDER_TYPE_CHOICES[0][0],
    )

    page_data = queries.delivery_page_data(order, order_type=selected_order_type)

    return render(request, "orders/manage_delivery.html", {
        "order": order,
        "form": form,
        "selected_order_type": selected_order_type,
        "delivery_order_type_choices": DeliveryDetail.ORDER_TYPE_CHOICES,
        **page_data,
        "unpriced_products": queries.get_unpriced_products(order.area),
    })


def _manage_delivery_with_type(request, order_id, order_type):
    order = get_object_or_404(OrderDetails, pk=order_id)

    if request.method == "POST":
        services.set_delivery_order_type(
            session=request.session,
            order=order,
            order_type=order_type,
        )

    return redirect("manage_delivery", order_id=order.id)


@login_required
def manage_delivery_mload(request, order_id):
    return _manage_delivery_with_type(request, order_id, "MLOAD")


@login_required
def manage_delivery_mret(request, order_id):
    return _manage_delivery_with_type(request, order_id, "MRET")


@login_required
def manage_delivery_vbo(request, order_id):
    return _manage_delivery_with_type(request, order_id, "VBO")

@login_required
def set_delivery_order_type(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)

    if request.method == "POST":
        services.set_delivery_order_type(
            session=request.session,
            order=order,
            order_type=request.POST.get("order_type"),
        )
    return HttpResponse(status=204)

@permission_required_redirect("orders.delete_orderdetails")
def delivery_delete(request, order_id, line_id):
    order = get_object_or_404(OrderDetails, pk=order_id)

    line = get_object_or_404(DeliveryDetail, pk=line_id, order=order)

    if request.method == "POST":
        services.delete_delivery_line(line, order)

        messages.success(request, "Delivery line removed.")
    return redirect("manage_delivery", order_id=order.id)

@login_required
def product_search(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)

    query = request.GET.get("q", "").strip()
    product = queries.find_product_for_area(order.area, query)

    return render(request, "orders/components/delivery/partials/product_result.html", {
        "product": product,
        "query": query,
    })

# ============================================================
# Transactions
# ============================================================

@login_required
def manage_transactions(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)

    order_type_key = f"transaction_order_type_{order.id}"
    customer_key = f"transaction_customer_{order.id}"
    invoice_type_key = f"transaction_invoice_type_{order.id}"

    selected_customer_id = request.session.get(customer_key)

    if request.method == "POST":
        form = TransactionLineForm(request.POST, order=order)

        if form.is_valid():
            try:
                services.add_transaction_line(
                    customer_detail=form.cleaned_data["customer_detail"],
                    product=form.cleaned_data["product"],
                    order_type=form.cleaned_data["order_type"],
                    quantity=form.cleaned_data["quantity"],
                    invoice_type=form.cleaned_data["invoice_type"],
                )
                request.session[order_type_key] = form.cleaned_data["order_type"]
                request.session[customer_key] = form.cleaned_data["customer_detail"].id
                request.session[invoice_type_key] = form.cleaned_data["invoice_type"]

                messages.success(request, "Transaction line added.")

                return redirect("manage_transactions", order_id=order.id)

            except ValueError as e:
                messages.error(request, str(e))
                form = TransactionLineForm(order=order)
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        selected_order_type = request.session.get(
            order_type_key,
            TransactionDetail.ORDER_TYPE_CHOICES[0][0],
        )
        selected_invoice_type = request.session.get(
            invoice_type_key,
            "CHARGE",
        )

        initial = {
            "order_type": selected_order_type,
            "invoice_type": selected_invoice_type,
        }
        if selected_customer_id:
            initial["customer_detail"] = selected_customer_id

        form = TransactionLineForm(order=order, initial=initial)

    # Refresh in case it changed during POST handling above
    selected_customer_id = request.session.get(customer_key)

    page_data = queries.transaction_page_data(
        order,
        customer_id=selected_customer_id,
    )

    return render(request, "orders/manage_transactions.html", {
        "order": order,
        "form": form,

        **page_data,

        "unpriced_products": (
            queries.get_unpriced_products(
                order.area
            )
        ),
    })


@login_required
def manage_transactions_for_customer(request, order_id, customer_detail_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    customer_detail = get_object_or_404(
        CustomerDetails, pk=customer_detail_id, order=order
    )

    if request.method == "POST":
        customer_name = customer_detail.customer.customer_business_name or ""

        if customer_name.strip().lower() == "cash":
            invoice_type = "CASH"
        else:
            invoice_type = "CHARGE"

        services.update_transaction_context(
            session=request.session,
            order=order,
            customer_detail_id=str(customer_detail.id),
            invoice_type=invoice_type,
        )

    return redirect("manage_transactions", order_id=order.id)


@login_required
def set_transaction_context(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)

    if request.method == "POST":
        services.update_transaction_context(
            session=request.session,
            order=order,
            order_type=request.POST.get("order_type"),
            invoice_type=request.POST.get("invoice_type"),
            customer_detail_id=request.POST.get("customer_detail"),
        )
    return HttpResponse(status=204)


@login_required
def save_invoice_balance(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    customer_key = f"transaction_customer_{order.id}"
    selected_customer_id = request.session.get(customer_key)

    if request.method == "POST" and selected_customer_id:
        customer_detail = get_object_or_404(
            CustomerDetails,
            pk=selected_customer_id,
            order=order,
        )

        customer_detail.invoice_balance = (
            request.POST.get("invoice_balance") or None
        )
        customer_detail.save(update_fields=["invoice_balance"])

    return HttpResponse(status=204)


@permission_required_redirect("orders.delete_orderdetails")
def transaction_delete(request, order_id, line_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    line = get_object_or_404(TransactionDetail, pk=line_id, customer_detail__order=order)

    if request.method == "POST":
        services.delete_transaction_line(line, order)

        messages.success(request, "Transaction line removed.")

    return redirect("manage_transactions", order_id=order.id)

@login_required
def transaction_customer_search(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    query = request.GET.get("invoice", "").strip()
    customer_detail = None

    if query:
        try:
            invoice_no = int(query)
        except ValueError:
            invoice_no = None
        if invoice_no is not None:
            customer_detail = (
                queries.get_customer_by_invoice(
                    order,
                    invoice_no,
                )
            )
    return render(request, "orders/components/transactional/partials/customer_result.html", {
        "customer_detail": customer_detail,
        "query": query,
    })

@login_required
def transaction_product_search(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    query = request.GET.get("q", "").strip()

    product = queries.find_product_for_area(order.area, query)

    return render(request, "orders/components/transactional/partials/product_result.html", {
        "product": product,
        "query": query,
    })

# ============================================================
# Customers
# ============================================================

@login_required
def add_customer(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)

    if request.method == "POST":
        form = CustomerDetailForm(request.POST, area=order.area)
        if form.is_valid():
            services.add_customer_to_order(order, form)

            messages.success(request, "Customer added to order.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    return redirect("order_detail", order_id=order.id)

@permission_required_redirect("orders.delete_orderdetails")
def customer_delete(request, order_id, customer_detail_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    customer_detail = get_object_or_404(CustomerDetails, pk=customer_detail_id, order=order)

    if request.method == "POST":
        services.delete_customer_from_order(customer_detail, order)

        messages.success(request, "Invoice removed.")

    return redirect("order_detail", order_id=order.id)

@login_required
def customer_search(request, order_id):
    search = request.GET.get("search", "").strip()

    customers = queries.search_customers(search)
    return render(request, "orders/components/details/partials/customer_select.html", {
        "customers": customers,
    })