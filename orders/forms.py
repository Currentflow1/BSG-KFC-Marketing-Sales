from typing import cast

from django import forms

from .models import (
    OrderDetails,
    CustomerDetails,
    DeliveryDetail,
    TransactionDetail,
    MarketingDetails,
)

from customers.models import Customer
from products.models import Product
from area_prices.models import AreaPrice

FIELD_CLASS = "w-full rounded-lg border border-gray-300 px-4 py-2"


# ---------------------------------------------------------------------------
# Custom fields
# ---------------------------------------------------------------------------

class ProductCodeChoiceField(forms.ModelChoiceField):
    """
    Display the product code while still returning the actual Product object.
    """

    def label_from_instance(self, obj):
        return obj.product_code


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------

class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderDetails
        fields = [
            "control_no",
            "area",
            "agent",
            "mload_date",
            "mret_date",
        ]

        widgets = {
            "control_no": forms.TextInput(
                attrs={"class": FIELD_CLASS}
            ),
            "area": forms.Select(
                attrs={"class": FIELD_CLASS}
            ),
            "agent": forms.Select(
                attrs={"class": FIELD_CLASS}
            ),
            "mload_date": forms.DateInput(
                attrs={
                    "class": FIELD_CLASS,
                    "type": "date",
                }
            ),
            "mret_date": forms.DateInput(
                attrs={
                    "class": FIELD_CLASS,
                    "type": "date",
                }
            ),
        }


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

class CustomerDetailForm(forms.ModelForm):
    class Meta:
        model = CustomerDetails
        fields = [
            "customer",
            "invoice_no",
        ]

        widgets = {
            "customer": forms.Select(
                attrs={
                    "class": FIELD_CLASS,
                    "autofocus": True,
                }
            ),
            "invoice_no": forms.NumberInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "Enter invoice number...",
                }
            ),
        }

    def __init__(self, *args, area=None, **kwargs):
        super().__init__(*args, **kwargs)

        customer_field = cast(
            forms.ModelChoiceField,
            self.fields["customer"],
        )

        if area is None:
            customer_field.queryset = Customer.objects.none()
            return

        customer_field.queryset = (
            Customer.objects
            .filter(customer_area=area)
            .order_by("customer_business_name")
        )


# ---------------------------------------------------------------------------
# Delivery lines
# ---------------------------------------------------------------------------

class DeliveryLineForm(forms.Form):

    order_type = forms.ChoiceField(
        choices=DeliveryDetail.ORDER_TYPE_CHOICES,
        widget=forms.Select(
            attrs={"class": FIELD_CLASS}
        ),
    )

    product = ProductCodeChoiceField(
        queryset=Product.objects.none(),
        widget=forms.HiddenInput(),
    )

    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": FIELD_CLASS,
                "autocomplete": "off",
            }
        ),
    )

    remarks = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": FIELD_CLASS}
        ),
    )

    def __init__(self, *args, area=None, **kwargs):
        super().__init__(*args, **kwargs)

        product_field = cast(
            ProductCodeChoiceField,
            self.fields["product"],
        )

        if area is None:
            product_field.queryset = Product.objects.none()
            return

        product_field.queryset = (
            Product.objects.filter(
                pk__in=AreaPrice.objects.filter(
                    area_name=area
                ).values("product_name")
            )
            .order_by("product_code")
        )


# ---------------------------------------------------------------------------
# Transaction lines
# ---------------------------------------------------------------------------

class TransactionLineForm(forms.Form):

    customer_detail = forms.ModelChoiceField(
        queryset=CustomerDetails.objects.none(),
        label="Customer / Invoice",
        widget=forms.HiddenInput(),
    )

    order_type = forms.ChoiceField(
        choices=TransactionDetail.ORDER_TYPE_CHOICES,
        widget=forms.Select(
            attrs={"class": FIELD_CLASS},
        ),
    )

    invoice_type = forms.ChoiceField(
        choices=TransactionDetail.INVOICE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={"class": FIELD_CLASS},
        ),
    )

    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        widget=forms.HiddenInput(),
    )

    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": FIELD_CLASS,
                "autocomplete": "off",
            },
        ),
    )

    remarks = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": FIELD_CLASS},
        ),
    )

    def __init__(self, *args, order=None, **kwargs):
        super().__init__(*args, **kwargs)

        product_field = cast(
            forms.ModelChoiceField,
            self.fields["product"],
        )

        customer_detail_field = cast(
            forms.ModelChoiceField,
            self.fields["customer_detail"],
        )

        if order is None:
            product_field.queryset = Product.objects.none()
            customer_detail_field.queryset = (
                CustomerDetails.objects.none()
            )
            return

        product_field.queryset = Product.objects.filter(
            pk__in=AreaPrice.objects.filter(
                area_name=order.area
            ).values("product_name")
        ).order_by("product_code")

        customer_detail_field.queryset = (
            order.customers
            .order_by("invoice_no")
        )


# ---------------------------------------------------------------------------
# Marketing details
# ---------------------------------------------------------------------------

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
            "product": forms.Select(
                attrs={"class": FIELD_CLASS}
            ),
            "total_SO": forms.NumberInput(
                attrs={"class": FIELD_CLASS}
            ),
            "total_SAM": forms.NumberInput(
                attrs={"class": FIELD_CLASS}
            ),
            "total_CBO": forms.NumberInput(
                attrs={"class": FIELD_CLASS}
            ),
            "total_CRET": forms.NumberInput(
                attrs={"class": FIELD_CLASS}
            ),
            "total_MLOAD": forms.NumberInput(
                attrs={"class": FIELD_CLASS}
            ),
            "total_MRET": forms.NumberInput(
                attrs={"class": FIELD_CLASS}
            ),
            "total_VBO": forms.NumberInput(
                attrs={"class": FIELD_CLASS}
            ),
        }