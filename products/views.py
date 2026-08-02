from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm

# Create your views here.
def product_list(request):
  products = Product.objects.all()
  return render(request, 'products/home.html', {
    'products': products
  })

def product_new(request):
  form = ProductForm(request.POST or None)

  if request.method == 'POST' and form.is_valid():
    form.save()
    return redirect('product_list')

  return render(request, 'products/new.html', {
    'form': form 
  })

def product_edit(request, id):
  product = get_object_or_404(Product, product_id=id)

  form = ProductForm(
    request.POST or None, 
    instance=product
  )

  if request.method == 'POST' and form.is_valid():
    form.save()
    return redirect('product_list')

  return render(request, 'products/edit.html', {
    'form': form
  })

def product_delete(request, id):
    product = get_object_or_404(Product, product_id=id)

    if request.method == "POST":
        product.delete()
        return redirect("product_list")

    return render(request, "products/delete.html", {
        "product": product
    })