from django.shortcuts import render, redirect, get_object_or_404

from . import services
from .models import Product
from .forms import ProductForm


def product_list(request):
    search = request.GET.get("search", "").strip()
    products = services.search_products(search)

    return render(request, "products/home.html", {
        "products": products,
    })


def product_search(request):
    search = request.GET.get("search", "").strip()
    products = services.search_products(search)

    return render(request, "products/components/list.html", {
        "products": products,
    })


def product_new(request):
    form = ProductForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("product_list")

    return render(request, "products/new.html", {
        "form": form,
    })


def product_edit(request, id):
    product = get_object_or_404(Product, product_id=id)

    form = ProductForm(request.POST or None, instance=product)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("product_list")

    return render(request, "products/edit.html", {
        "form": form,
        "product": product,
    })


def product_delete(request, id):
    product = get_object_or_404(Product, product_id=id)

    if request.method == "POST":
        product.delete()
        return redirect("product_list")

    return render(request, "products/delete.html", {
        "product": product,
    })