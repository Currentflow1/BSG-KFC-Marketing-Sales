from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from login.decorators import permission_required_redirect
from .models import OrderDetails, CustomerDetails, DeliveryDetail, TransactionDetail
from .forms import OrderForm, CustomerDetailForm, DeliveryLineForm, TransactionLineForm
from . import services


# ---------------------------------------------------------------------------
# Order list / detail
# ---------------------------------------------------------------------------

@login_required
def order_list(request):
    orders = services.search_orders(
        search=request.GET.get("search"),
        sort=request.GET.get("sort", "-beg_date"),
    )

    return render(request, "orders/home.html", {
        "orders": orders,
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        OrderDetails.objects.select_related(
            "area",
            "agent",
        ).prefetch_related(
            "customers__customer",
            "customers__transactions",
            "deliveries__product",
        ),
        pk=order_id,
    )
    customer_form = CustomerDetailForm(area=order.area)

    return render(
        request,
        "orders/detail.html",
        {
            "order": order,
            "customer_form": customer_form,
            "marketing_summary": services.get_marketing_summary(order),
            "unpriced_products": services.get_unpriced_products(order.area),
        },
    )


# ---------------------------------------------------------------------------
# Order CRUD
# ---------------------------------------------------------------------------

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
    return render(request, "orders/edit.html", {"form": form, "order": order})


@permission_required_redirect("orders.delete_orderdetails")
def order_delete(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    if request.method == "POST":
        order.delete()
        messages.success(request, "Order deleted.")
        return redirect("order_list")
    return render(request, "orders/delete.html", {"order": order})


@permission_required_redirect("orders.change_orderdetails")
def order_complete(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    if request.method == "POST":
        services.complete_order(order)
        messages.success(request, f"Order {order.control_no} marked complete.")
    return redirect("order_detail", order_id=order.id)


@permission_required_redirect("orders.change_orderdetails")
def order_uncomplete(request, order_id):
    """Undo an accidental 'Complete' — just clears end_date, nothing else changes."""
    order = get_object_or_404(OrderDetails, pk=order_id)
    if request.method == "POST":
        order.end_date = None
        order.save(update_fields=["end_date"])
        messages.success(request, f"Order {order.control_no} reopened.")
    return redirect("order_detail", order_id=order.id)


# ---------------------------------------------------------------------------
# Delivery lines
# ---------------------------------------------------------------------------

@login_required
def manage_delivery(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    if request.method == "POST":
        form = DeliveryLineForm(request.POST, area=order.area)
        if form.is_valid():
            try:
                services.add_delivery_line(
                    order=order,
                    product=form.cleaned_data["product"],
                    order_type=form.cleaned_data["order_type"],
                    quantity=form.cleaned_data["quantity"],
                    remarks=form.cleaned_data["remarks"],
                )
                messages.success(request, "Delivery line added.")
            except ValueError as e:
                messages.error(request, str(e))
            return redirect("manage_delivery", order_id=order.id)
    else:
        form = DeliveryLineForm(area=order.area)

    return render(request, "orders/manage_delivery.html", {
        "order": order,
        "form": form,
        "lines": DeliveryDetail.objects.filter(order=order).select_related("product").order_by("-created_at"),
        "totals": services.get_delivery_totals(order),
        "unpriced_products": services.get_unpriced_products(order.area),
    })


@permission_required_redirect("orders.delete_orderdetails")
def delivery_delete(request, order_id, line_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    line = get_object_or_404(DeliveryDetail, pk=line_id, order=order)

    if request.method == "POST":
        line.delete()
        services.sync_marketing_details(order)
        messages.success(request, "Delivery line removed.")

    return redirect("manage_delivery", order_id=order.id)


# ---------------------------------------------------------------------------
# Transaction lines
# ---------------------------------------------------------------------------

@login_required
def manage_transactions(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
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
                    remarks=form.cleaned_data["remarks"],
                )
                messages.success(request, "Transaction line added.")
            except ValueError as e:
                messages.error(request, str(e))
            return redirect("manage_transactions", order_id=order.id)
    else:
        form = TransactionLineForm(order=order)

    return render(request, "orders/manage_transactions.html", {
        "order": order,
        "form": form,
        "lines": TransactionDetail.objects.filter(customer_detail__order=order)
                    .select_related("product", "customer_detail__customer")
                    .order_by("-created_at"),
        "totals": services.get_transaction_totals(order),
        "unpriced_products": services.get_unpriced_products(order.area),
    })


@permission_required_redirect("orders.delete_orderdetails")
def transaction_delete(request, order_id, line_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    line = get_object_or_404(
        TransactionDetail,
        pk=line_id,
        customer_detail__order=order,
    )

    if request.method == "POST":
        line.delete()
        services.sync_marketing_details(order)
        messages.success(request, "Transaction line removed.")

    return redirect("manage_transactions", order_id=order.id)


# ---------------------------------------------------------------------------
# Customers on an order
# ---------------------------------------------------------------------------

@login_required
def add_customer(request, order_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    if request.method == "POST":
        form = CustomerDetailForm(request.POST, area=order.area)
        if form.is_valid():
            cd = form.save(commit=False)
            cd.order = order
            cd.save()
            services.sync_marketing_details(order)
            messages.success(request, "Customer added to order.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    return redirect("order_detail", order_id=order.id)


@permission_required_redirect("orders.delete_orderdetails")
def customer_delete(request, order_id, customer_detail_id):
    order = get_object_or_404(OrderDetails, pk=order_id)
    customer_detail = get_object_or_404(
        CustomerDetails,
        pk=customer_detail_id,
        order=order,
    )

    if request.method == "POST":
        customer_detail.delete()
        services.sync_marketing_details(order)
        messages.success(request, "Invoice removed.")

    return redirect("order_detail", order_id=order.id)