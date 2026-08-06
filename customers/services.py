from django.db.models import Q
from .models import Customer

def search_customers(search=None):
    customers = Customer.objects.all()

    if search:
        customers = customers.filter(
            Q(customer_business_name__icontains=search) |
            Q(customer_contact_person__icontains=search) |
            Q(customer_mobile_no__icontains=search) |
            Q(customer_business_address__icontains=search)
        )

        
        if search.lower() in ["active", "false", "no"]:
            customers = customers | Customer.objects.filter(discontinued=False)

        customers = customers.distinct()

    return customers