from django.db.models import Q
from .models import Employee


def search_employees(search=None):
    employees = Employee.objects.all()

    if search:
        employees = employees.filter(
            Q(employee_name__icontains=search) |
            Q(employee_nickname__icontains=search) |
            Q(employee_group__icontains=search) |
            Q(employee_position__icontains=search) |
            Q(employee_birthdate__icontains=search) |
            Q(employee_hiredate__icontains=search) |
            Q(employee_sex__icontains=search) |
            Q(employee_sss__icontains=search) |
            Q(employee_gsis__icontains=search)
        )

        if search.lower() in ["active", "true", "yes"]:
            employees = employees | Employee.objects.filter(employeeActive=True)

        elif search.lower() in ["inactive", "false", "no"]:
            employees = employees | Employee.objects.filter(employeeActive=False)

        employees = employees.distinct()

    return employees