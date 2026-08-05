from typing import cast
from django import forms
from .models import OrderDetails, CustomerDetails, DeliveryDetail, TransactionDetail, MarketingDetails

FIELD_CLASS = "w-full rounded-lg border border-gray-300 px-4 py-2"

class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderDetails
        fields = [
            "control_no",
            "area",
            "agent",
            "van_number",
            "beg_date",
            "mload_date",
            "mret_date",
            "end_date",
        ]

        widgets = {
            "control_no": forms.TextInput(attrs={"class": FIELD_CLASS}),
            "area": forms.Select(attrs={"class": FIELD_CLASS}),
            "agent": forms.Select(attrs={"class": FIELD_CLASS}),
            "van_number": forms.NumberInput(attrs={"class": FIELD_CLASS}),

            "beg_date": forms.DateInput(
                attrs={"class": FIELD_CLASS, "type": "date"}
            ),
            "mload_date": forms.DateInput(
                attrs={"class": FIELD_CLASS, "type": "date"}
            ),
            "mret_date": forms.DateInput(
                attrs={"class": FIELD_CLASS, "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": FIELD_CLASS, "type": "date"}
            ),
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
        if area is not None:
            customer_field = cast(forms.ModelChoiceField, self.fields["customer"])
            if customer_field.queryset is not None:
                customer_field.queryset = customer_field.queryset.filter(customer_area=area)


class DeliveryLineForm(forms.Form):
    """Quantity and price are computed in services.add_delivery_line — this form
    only collects what a person actually chooses."""
    order_type = forms.ChoiceField(
        choices=DeliveryDetail.ORDER_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": FIELD_CLASS}),
    )
    product = forms.ModelChoiceField(
        queryset=None,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from products.models import Product
        product_field = cast(forms.ModelChoiceField, self.fields["product"])
        product_field.queryset = Product.objects.all()


class TransactionLineForm(forms.Form):
    """Scoped to one customer's invoice (customer_detail) within the order."""
    customer_detail = forms.ModelChoiceField(
        queryset=None,
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
        queryset=None,
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
        product_field = cast(forms.ModelChoiceField, self.fields["product"])
        product_field.queryset = Product.objects.all()
        if order is not None:
            customer_detail_field = cast(forms.ModelChoiceField, self.fields["customer_detail"])
            customer_detail_field.queryset = order.customers.all()


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