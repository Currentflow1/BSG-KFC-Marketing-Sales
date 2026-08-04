from typing import cast
from django import forms
from .models import OrderDetails, CustomerDetails


class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderDetails
        fields = ["control_no", "area", "agent", "van_number"]
        widgets = {
            "control_no": forms.TextInput(attrs={"class": "w-full rounded border border-gray-300 px-3 py-2"}),
            "area": forms.Select(attrs={"class": "w-full rounded border border-gray-300 px-3 py-2"}),
            "agent": forms.Select(attrs={"class": "w-full rounded border border-gray-300 px-3 py-2"}),
            "van_number": forms.NumberInput(attrs={"class": "w-full rounded border border-gray-300 px-3 py-2"}),
        }


class CustomerDetailForm(forms.ModelForm):
    class Meta:
        model = CustomerDetails
        fields = ["customer", "invoice_no"]
        widgets = {
            "customer": forms.Select(attrs={"class": "w-full rounded border border-gray-300 px-3 py-2"}),
            "invoice_no": forms.NumberInput(attrs={"class": "w-full rounded border border-gray-300 px-3 py-2"}),
        }

    def __init__(self, *args, area=None, **kwargs):
        super().__init__(*args, **kwargs)
        if area is not None:
            customer_field = cast(forms.ModelChoiceField, self.fields["customer"])
            if customer_field.queryset is not None:
                customer_field.queryset = customer_field.queryset.filter(customer_area=area)