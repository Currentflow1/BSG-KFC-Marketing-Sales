from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from products.models import Product
from orders.models import OrderDetails, CustomerDetails, DeliveryDetail, TransactionDetail

from .middleware import get_current_user
from .models import TransactionLog

TRACKED_MODELS = [
    Product,
    OrderDetails,
    CustomerDetails,
    DeliveryDetail,
    TransactionDetail,
]


def _log(sender, instance, action):
    user = get_current_user()
    TransactionLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        model_name=sender.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
    )


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if sender in TRACKED_MODELS:
        _log(sender, instance, "CREATE" if created else "UPDATE")


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender in TRACKED_MODELS:
        _log(sender, instance, "DELETE")