from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from area_prices.models import Area
from employees.models import Employee
from customers.models import Customer
from .models import OrderDetails, CustomerDetails
from .forms import OrderForm, CustomerDetailForm
from . import services


def order_list(request):
    orders = services.search_orders(
        control_no=request.GET.get("control_no"),
        area_id=request.GET.get("area"),
        agent_id=request.GET.get("agent"),
        product_id=request.GET.get("product"),
        van_number=request.GET.get("van_number"),
        sort=request.GET.get("sort", "-beg_date"),
    )
    return render(request, "orders/home.html", {"orders": orders})


def order_detail(request, order_id):
    order = get_object_or_404(OrderDetails, id=order_id)
    customer_form = CustomerDetailForm(area=order.area)
    return render(request, "orders/detail.html", {
        "order": order,
        "customer_form": customer_form,
        "marketing_summary": services.get_marketing_summary(order),
    })

def order_new(request):
    form = OrderForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        order = form.save()
        messages.success(request, f"Order {order.control_no} created.")
        return redirect('order_list')

    return render(request, 'orders/new.html', { 'form': form })

def order_edit(request, order_id): 
    order = get_object_or_404(OrderDetails, id=order_id)

    form  = OrderForm(
        request.POST or None,
        instance=order
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Order {order.control_no} updated.")
        return redirect('order_list')

    return render(request, 'orders/edit.html', { 'form': form, 'order': order })

def order_delete(request, order_id):
    order = get_object_or_404(OrderDetails, id=order_id)
    if request.method == "POST":
        order.delete()
        messages.success(request, "Order deleted.")
        return redirect("order_list")
    return render(request, "orders/delete.html", {"order": order})


def order_complete(request, order_id):
    order = get_object_or_404(OrderDetails, id=order_id)
    if request.method == "POST":
        services.complete_order(order)
        messages.success(request, f"Order {order.control_no} marked complete.")
    return redirect("order_detail", order_id=order.id)


def add_customer(request, order_id):
    order = get_object_or_404(OrderDetails, id=order_id)
    if request.method == "POST":
        form = CustomerDetailForm(request.POST, area=order.area)
        if form.is_valid():
            cd = form.save(commit=False)
            cd.order = order
            cd.save()
            messages.success(request, "Customer added to order.")
        else:
            messages.error(request, "Could not add customer — check the form.")
    return redirect("order_detail", order_id=order.id)