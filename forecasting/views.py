from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from products.models import Product
from .services import ForecastService, InsufficientHistoryError


def dashboard(request):
    search = request.GET.get("search", "").strip()

    products = Product.objects.filter(discontinued=False)

    if search:
        products = products.filter(
            Q(product_code__icontains=search)
            | Q(product_name__icontains=search)
        )

    return render(request, "forecasting/dashboard.html", {
        "products": products
    })


def forecasting_search(request):
    search = request.GET.get("search", "").strip()
    products = Product.objects.filter(discontinued=False)

    if search:
        products = products.filter(
            Q(product_code__icontains=search)|
            Q(product_name__icontains=search)
        )

    return render(
        request,
        "forecasting/components/product_list.html",
        {
            "products": products,
        },
    )


def product_forecast(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    horizon = int(request.GET.get("days", 30))
    force_refresh = request.GET.get("refresh") == "1"

    service = ForecastService()

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

    # HTMX request: return the forecast table AND the summary/recommendation
    # cards together, all computed from THIS request's horizon. Previously
    # only forecast_result.html was returned and only #forecast-result was
    # swapped, so summary.html / recommendation.html kept showing whatever
    # horizon the page last fully loaded with (forecast_total, safety_stock,
    # recommended_stock, history_days, etc.) while the forecast table showed
    # the newly selected horizon's rows — the two would visibly disagree
    # after every Refresh with a changed horizon. forecast_result.html now
    # includes the summary/recommendation partials so everything updates
    # together; the hx-target/hx-swap in settings.html must wrap all three
    # cards (see forecast_result.html) for this to take effect.
    if request.headers.get("HX-Request"):
        return render(
            request,
            "forecasting/components/forecast_result.html",
            {
                "forecast": forecast,
                "summary": summary,
                "error": error,
            },
        )

    # Normal request: return the entire page
    return render(
        request,
        "forecasting/product_forecast.html",
        {
            "product": product,
            "history": service.history_for_display(product_id),
            "forecast": forecast,
            "summary": summary,
            "horizon": horizon,
            "error": error,
        },
    )