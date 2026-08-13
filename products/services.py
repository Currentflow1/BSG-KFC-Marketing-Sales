from django.db.models import Q
from .models import Product


def search_products(search=None):
    products = Product.objects.all()

    if search:
        search = search.strip()

        if search:
            products = products.filter(
                Q(product_code__icontains=search)| 
                Q(product_name__icontains=search)| 
                Q(factory_price__icontains=search)| 
                Q(shelf_life__icontains=search)| 
                Q(product_packaging__icontains=search)
            )

            search_lower = search.lower()

            if search_lower in ["discontinued", "true", "yes"]:
                products = Product.objects.filter(
                    Q(product_code__icontains=search)| 
                    Q(product_name__icontains=search)| 
                    Q(factory_price__icontains=search)| 
                    Q(shelf_life__icontains=search)| 
                    Q(product_packaging__icontains=search)| 
                    Q(discontinued=True)
                )

            elif search_lower in ["active", "false", "no"]:
                products = Product.objects.filter(
                    Q(product_code__icontains=search)| 
                    Q(product_name__icontains=search)| 
                    Q(factory_price__icontains=search)| 
                    Q(shelf_life__icontains=search)| 
                    Q(product_packaging__icontains=search)| 
                    Q(discontinued=False)
                )

    return products.order_by("product_code")