from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import TransactionLog


@login_required
def home(request):
    logs = TransactionLog.objects.select_related("user").all()[:200]
    return render(request, "transaction_logs/home.html", {"logs": logs})