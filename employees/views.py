from django.shortcuts import render, redirect, get_object_or_404
from . import services
from .models import Employee
from .forms import EmployeeForm

# Create your views here.

def employee_list(request):
    employees = services.search_employees(
        request.GET.get("search")
    )

    return render(request, "employees/home.html", {
      "employees": employees,
    })

def employee_search(request):
    search = request.GET.get("search", "").strip()
    employees = services.search_employees(search)

    return render(request, "employees/components/list.html", {
      "employees": employees,
    })

def employee_new(request):
  form = EmployeeForm(request.POST or None)

  if request.method == 'POST' and form.is_valid():
    form.save()
    return redirect('employee_list')

  return render(request, 'employees/new.html', {
    'form': form
  })

def employee_edit(request, id):
  employee = get_object_or_404(Employee, employee_id=id)

  form = EmployeeForm(
    request.POST or None,
    instance=employee
  )

  if request.method == 'POST' and form.is_valid():
    form.save()
    return redirect('employee_list')

  return render(request, 'employees/edit.html' , {
    'form': form,
    'employee': employee
  })


def employee_delete(request, id):
  employee = get_object_or_404(Employee, employee_id=id)

  if request.method == 'POST':
    employee.delete()
    return redirect('employee_list')

  return render(request, 'employees/delete.html')