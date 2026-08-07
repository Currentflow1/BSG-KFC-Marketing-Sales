from django.shortcuts import get_object_or_404, render
from products.models import Product
from .services import ForecastService, InsufficientHistoryError


def dashboard(request):
    search = request.GET.get("search", "").strip()

    products = Product.objects.filter(discontinued=False)

    if search:
        products = products.filter(
            product_name__icontains=search
        )

    return render(
        request,
        "forecasting/dashboard.html",
        {"products": products},
    )


def product_forecast(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    horizon = int(request.GET.get("days", 30))
    force_refresh = request.GET.get("refresh") == "1"

    service = ForecastService()

    history = service.history_for_display(product_id)

    forecast = []
    summary = None
    error = None

    try:
        forecast = service.get_or_create_forecast(
            product_id=product_id,
            horizon=horizon,
            force_refresh=force_refresh,
        )

        summary = service.get_summary(
            product_id,
            forecast,
        )

    except InsufficientHistoryError as exc:
        error = str(exc)

    return render(
        request,
        "forecasting/product_forecast.html",
        {
            "product": product,
            "history": history,
            "forecast": forecast,
            "summary": summary,
            "horizon": horizon,
            "error": error,
        },
    )