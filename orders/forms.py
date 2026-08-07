from typing import cast
from django import forms

from .models import (
    OrderDetails,
    CustomerDetails,
    DeliveryDetail,
    TransactionDetail,
    MarketingDetails,
)
from products.models import Product
from area_prices.models import AreaPrice

FIELD_CLASS = "w-full rounded-lg border border-gray-300 px-4 py-2"


class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderDetails
        fields = [
            "control_no",
            "area",
            "agent",
            "van_number",
        ]
        widgets = {
            "control_no": forms.TextInput(attrs={"class": FIELD_CLASS}),
            "area": forms.Select(attrs={"class": FIELD_CLASS}),
            "agent": forms.Select(attrs={"class": FIELD_CLASS}),
            "van_number": forms.NumberInput(attrs={"class": FIELD_CLASS}),
        }


class CustomerDetailForm(forms.ModelForm):
    class Meta:
        model = CustomerDetails
        fields = ["customer", "invoice_no"]
        widgets = {
            "customer": forms.Select(attrs={"class": FIELD_CLASS}),
            "invoice_no": forms.NumberInput(attrs={"class": FIELD_CLASS}),
        }

    def __init__(self, *args, area=None, **kwargs):
        super().__init__(*args, **kwargs)

        customer_field = cast(forms.ModelChoiceField, self.fields["customer"])

        if area is not None:
            customer_field.queryset = customer_field.queryset.filter(
                customer_area=area
            )


class DeliveryLineForm(forms.Form):
    order_type = forms.ChoiceField(
        choices=DeliveryDetail.ORDER_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": FIELD_CLASS}),
    )

    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        widget=forms.Select(attrs={"class": FIELD_CLASS}),
    )

    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": FIELD_CLASS}),
    )

    remarks = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": FIELD_CLASS}),
    )

    def __init__(self, *args, area=None, **kwargs):
        super().__init__(*args, **kwargs)

        from products.models import Product
        from area_prices.models import AreaPrice

        product_field = cast(forms.ModelChoiceField, self.fields["product"])

        if area is None:
            product_field.queryset = Product.objects.none()
            return

        product_field.queryset = Product.objects.filter(
            pk__in=AreaPrice.objects.filter(
                area_name=area
            ).values("product_name")
        ).order_by("product_name")


class TransactionLineForm(forms.Form):
    customer_detail = forms.ModelChoiceField(
        queryset=CustomerDetails.objects.none(),
        label="Customer / Invoice",
        widget=forms.Select(attrs={"class": FIELD_CLASS}),
    )

    order_type = forms.ChoiceField(
        choices=TransactionDetail.ORDER_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": FIELD_CLASS}),
    )

    invoice_type = forms.ChoiceField(
        choices=TransactionDetail.INVOICE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": FIELD_CLASS}),
    )

    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        widget=forms.Select(attrs={"class": FIELD_CLASS}),
    )

    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": FIELD_CLASS}),
    )

    remarks = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": FIELD_CLASS}),
    )
    
    def __init__(self, *args, order=None, **kwargs):
        super().__init__(*args, **kwargs)

        from products.models import Product
        from area_prices.models import AreaPrice

        product_field = cast(forms.ModelChoiceField, self.fields["product"])
        customer_detail_field = cast(forms.ModelChoiceField, self.fields["customer_detail"])

        if order is None:
            product_field.queryset = Product.objects.none()
            customer_detail_field.queryset = CustomerDetails.objects.none()
            return

        product_field.queryset = Product.objects.filter(
            pk__in=AreaPrice.objects.filter(
                area_name=order.area
            ).values("product_name")
        ).order_by("product_name")

        customer_detail_field.queryset = order.customers.order_by("invoice_no")

class MarketingDetailsForm(forms.ModelForm):
    class Meta:
        model = MarketingDetails

        fields = [
            "product",
            "total_SO",
            "total_SAM",
            "total_CBO",
            "total_CRET",
            "total_MLOAD",
            "total_MRET",
            "total_VBO",
        ]

        widgets = {
            "product": forms.Select(attrs={"class": FIELD_CLASS}),
            "total_SO": forms.NumberInput(attrs={"class": FIELD_CLASS}),
            "total_SAM": forms.NumberInput(attrs={"class": FIELD_CLASS}),
            "total_CBO": forms.NumberInput(attrs={"class": FIELD_CLASS}),
            "total_CRET": forms.NumberInput(attrs={"class": FIELD_CLASS}),
            "total_MLOAD": forms.NumberInput(attrs={"class": FIELD_CLASS}),
            "total_MRET": forms.NumberInput(attrs={"class": FIELD_CLASS}),
            "total_VBO": forms.NumberInput(attrs={"class": FIELD_CLASS}),
        }