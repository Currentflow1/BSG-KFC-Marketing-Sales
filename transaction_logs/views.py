from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from . import services


@login_required
def home(request):
    logs = services.search_transaction_logs(
        search=request.GET.get("search"),
        date_from=request.GET.get("date_from"),
        date_to=request.GET.get("date_to"),
    )[:200]

    return render(request, "transaction_logs/home.html", {
        "logs": logs,
    })