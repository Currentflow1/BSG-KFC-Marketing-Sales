from django.shortcuts import render, redirect, get_object_or_404

from . import services
from .models import Area, AreaPrice
from .forms import AreaForm, AreaPriceForm


def area_price_list(request):
    return render(
        request,
        "area_prices/home.html",
        {
            "areas": services.search_areas(),
            "area_prices": services.search_area_prices(),
        },
    )


def area_search(request):
    search = request.GET.get("search", "").strip()

    areas = services.search_areas(search)

    return render(
        request,
        "area_prices/components/area/components/list.html",
        {
            "areas": areas,
        },
    )


def area_price_search(request):
    search = request.GET.get("search", "").strip()

    area_prices = services.search_area_prices(search)

    return render(
        request,
        "area_prices/components/list.html",
        {
            "area_prices": area_prices,
        },
    )


def area_new(request):
    form = AreaForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("area_price_list")

    return render(
        request,
        "area_prices/components/area/new_area.html",
        {
            "form": form,
        },
    )


def area_price_new(request):
    form = AreaPriceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("area_price_list")

    return render(
        request,
        "area_prices/new.html",
        {
            "form": form,
        },
    )


def area_edit(request, id):
    area = get_object_or_404(
        Area,
        area_id=id,
    )

    form = AreaForm(
        request.POST or None,
        instance=area,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("area_price_list")

    return render(
        request,
        "area_prices/components/area/edit_area.html",
        {
            "form": form,
        },
    )


def area_price_edit(request, id):
    area_price = get_object_or_404(
        AreaPrice,
        area_price_id=id,
    )

    form = AreaPriceForm(
        request.POST or None,
        instance=area_price,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("area_price_list")

    return render(
        request,
        "area_prices/edit.html",
        {
            "form": form,
        },
    )


def area_delete(request, id):
    area = get_object_or_404(
        Area,
        area_id=id,
    )

    if request.method == "POST":
        area.delete()
        return redirect("area_price_list")

    return render(
        request,
        "area_prices/components/area/delete_area.html",
        {
            "area": area,
        },
    )


def area_prices_delete(request, id):
    area_price = get_object_or_404(
        AreaPrice,
        area_price_id=id,
    )

    if request.method == "POST":
        area_price.delete()
        return redirect("area_price_list")

    return render(
        request,
        "area_prices/delete.html",
        {
            "area_prices": area_price,
        },
    )