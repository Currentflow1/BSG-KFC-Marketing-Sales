from django.db.models import Q

from .models import TransactionLog


def search_transaction_logs(search=None, date_from=None, date_to=None):
    logs = TransactionLog.objects.select_related("user")

    if search:
        logs = logs.filter(
            Q(user__username__icontains=search) |
            Q(action__icontains=search) |
            Q(model_name__icontains=search) |
            Q(object_id__icontains=search) |
            Q(object_repr__icontains=search)
        )

    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)

    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)

    return logs.order_by("-timestamp")