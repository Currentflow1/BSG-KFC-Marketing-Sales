from django.db import transaction


@transaction.atomic
def complete_order(order):
    from datetime import date

    today = date.today()

    if today < order.beg_date:
        today = order.beg_date

    order.end_date = today
    order.save(update_fields=["end_date"])

    return order


@transaction.atomic
def reopen_order(order):
    order.end_date = None
    order.save(update_fields=["end_date"])

    return order


@transaction.atomic
def delete_order(order):
    order.delete()