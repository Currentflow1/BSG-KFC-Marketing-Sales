from django.db.models import Q
from .models import Product

def search_products(search=None):
    products = Product.objects.all()

    if search:
        products = products.filter(
            Q(product_code__icontains=search) |
            Q(product_name__icontains=search) |
            Q(factory_price__icontains=search) |
            Q(shelf_life__icontains=search) |
            Q(product_packaging__icontains=search)
        )

        if search.lower() in ["discontinued", "true", "yes"]:
            products = products | Product.objects.filter(discontinued=True)
        elif search.lower() in ["active", "false", "no"]:
            products = products | Product.objects.filter(discontinued=False)

        products = products.distinct()

    return products