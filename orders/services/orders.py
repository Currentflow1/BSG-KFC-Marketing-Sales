from django.db import transaction

@transaction.atomic
def delete_order(order):
    order.delete()