from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer
from .forms import CustomerForm

def customer_list(request):
  customers = Customer.objects.all()
  return render(request, 'customers/home.html', {
    'customers': customers
  })


def customer_new(request):
  form = CustomerForm(request.POST or None)

  if request.method == 'POST' and form.is_valid():
    form.save()
    return render(request, 'customer_list')

  return render (request, 'customers/new.html', {
    'form': form
  })


def customer_edit(request, id):
  customer = get_object_or_404(Customer, customer_id=id)

  form = CustomerForm(
    request.POST or None,
    instance=customer
  )

  if request.method == 'POST' and form.is_valid():
    form.save()
    return render(request, 'customer_list')

  return render(request, 'customers/edit.html', {
    'form': form
  })


def customer_delete(request, id):
  customer = get_object_or_404(Customer, customer_id=id)

  if request.method == 'POST':
    customer.delete()
    return render(request, 'customer_list')

  return render(request, 'customers/delete.html', {
    'customer': customer
  })
