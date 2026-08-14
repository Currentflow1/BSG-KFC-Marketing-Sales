from area_prices.models import AreaPrice


def get_area_price(area, product):
    try:
        return AreaPrice.objects.get(
            area_name=area,
            product_name=product,
        ).area_price
    except AreaPrice.DoesNotExist:
        raise ValueError(
            f"No price found for {product} in area {area}. "
            "Please add the area price first."
        )