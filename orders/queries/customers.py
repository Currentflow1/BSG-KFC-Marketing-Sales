from django.db.models import Q

from customers.models import Customer

from ..models import CustomerDetails


def get_selected_customer(order, customer_detail_id):
    return (
        CustomerDetails.objects
        .filter(
            pk=customer_detail_id,
            order=order,
        )
        .select_related("customer")
        .first()
    )


def customer_exists_on_order(order, customer_detail_id):
    return CustomerDetails.objects.filter(
        pk=customer_detail_id,
        order=order,
    ).exists()


def get_customer_by_invoice(order, invoice_no):
    return (
        CustomerDetails.objects
        .filter(
            order=order,
            invoice_no=invoice_no,
        )
        .select_related("customer")
        .first()
    )


def search_customers(search=""):
    customers = Customer.objects.all()

    if search:
        customers = customers.filter(
            Q(customer_business_name__icontains=search)
            | Q(customer_contact_person__icontains=search)
            | Q(customer_mobile_no__icontains=search)
        )

    return customers.order_by("customer_business_name")