from django.apps import AppConfig


class TransactionLogsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "transaction_logs"

    def ready(self):
        import transaction_logs.signals  # noqa: F401