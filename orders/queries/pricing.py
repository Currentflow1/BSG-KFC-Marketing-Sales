from area_prices.models import AreaPrice
from products.models import Product


def get_unpriced_products(area):
    priced_ids = (
        AreaPrice.objects
        .filter(area_name=area)
        .values_list("product_name_id", flat=True)
    )

    return Product.objects.exclude(
        pk__in=priced_ids
    )


def find_product_for_area(area, query):
    if not query:
        return None

    products = Product.objects.filter(
        pk__in=AreaPrice.objects.filter(
            area_name=area
        ).values("product_name")
    )

    product = (
        products
        .filter(product_code__iexact=query)
        .first()
    )

    if product is None:
        product = (
            products
            .filter(product_name__icontains=query)
            .order_by("product_code")
            .first()
        )

    return product