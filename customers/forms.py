from django import forms
from .models import Customer

FIELD_CLASS = "w-full rounded-lg border border-gray-300 px-4 py-2"

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "customer_area",
            "customer_business_name",
            "customer_contact_person",
            "customer_mobile_no",
            "customer_business_address",
            "customer_active",
        ]

        widgets = {
            "customer_area": forms.Select(attrs={
                "class": FIELD_CLASS,
            }),
            "customer_business_name": forms.TextInput(attrs={
                "class": FIELD_CLASS,
            }),
            "customer_contact_person": forms.TextInput(attrs={
                "class": FIELD_CLASS,
            }),
            "customer_mobile_no": forms.TextInput(attrs={
                "class": FIELD_CLASS,
            }),
            "customer_business_address": forms.TextInput(attrs={
                "class": FIELD_CLASS,
            }),
            "customer_active": forms.CheckboxInput(attrs={
                "class": "h-4 w-4 rounded border-gray-300",
            }),
        }