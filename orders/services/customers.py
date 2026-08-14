from django.db import transaction
from .marketing import sync_marketing_details


@transaction.atomic
def add_customer_to_order(order, form):
    customer_detail = form.save(commit=False)
    customer_detail.order = order
    customer_detail.save()

    sync_marketing_details(order)

    return customer_detail


@transaction.atomic
def delete_customer_from_order(customer_detail, order):
    customer_detail.delete()
    sync_marketing_details(order)