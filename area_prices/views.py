from django.shortcuts import render, redirect, get_object_or_404
from .models import Area
from .models import Area_price
from .forms import AreaForm
from .forms import AreaPriceForm


def area_price_list(request):
  area_prices = Area_price.objects.all()
  areas = Area.objects.all()
  return render(request, 'area_prices/home.html', {
    'area_prices': area_prices,
    'areas': areas,
    })


def area_new(request):
  form = AreaForm(request.POST or None)

  if request.method == 'POST' and form.is_valid():
    form.save()
    return redirect('area_price_list')

  return render(request, 'area_prices/components/area/new_area.html', {
    'form': form
  })


  
def area_price_new(request):
  form = AreaPriceForm(request.POST or None)

  if request.method == 'POST' and form.is_valid():
    form.save()
    return redirect('area_price_list')

  return render(request, 'area_prices/new.html', {
    'form': form
  })


def area_edit(request, id):
  area = get_object_or_404(Area, area_id=id)

  form = AreaForm(
    request.POST or None,
    instance=area
    )
  
  if request.method == 'POST' and form.is_valid():
    form.save()
    return redirect('area_price_list')

  return render(request, 'area_prices/components/area/edit_area.html', {
    'form': form
  })


def area_price_edit(request, id):
  area_price = get_object_or_404(Area_price, area_price_id=id)

  form = AreaPriceForm(
    request.POST or None,
    instance=area_price
    )
  
  if request.method == 'POST' and form.is_valid():
    form.save()
    return redirect('area_price_list')

  return render(request, 'area_prices/edit.html', {
    'form': form
  })
  


def area_delete(request, id):
  area = get_object_or_404(Area, area_id=id)

  if request.method == 'POST':
    area.delete()
    return redirect('area_price_list')

  return render(request, 'area_prices/components/area/delete_area.html', {
    'area': area
  })


def area_prices_delete(request, id):
  area_prices = get_object_or_404(Area_price, area_price_id=id)

  if request.method == 'POST':
    area_prices.delete()
    return redirect('area_price_list')

  return render(request, 'area_prices/delete.html', {
    'area_prices': area_prices
  })