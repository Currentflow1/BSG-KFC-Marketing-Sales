from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
  class Meta:
    model = Customer
    field = [
      'customer_area',
      'customer_business_name',
      'customer_contact_person',
      'customer_mobile_no'
      'customer_business_address'
      'customer_active'
    ]

    widget = {
      'customer_area': forms.Select(attrs={
        "class": "w-50 rounded-lg border px-3 py-2",
      }),
      'customer_business_name': forms.TextInput(attrs={
        "class": "w-full rounded-lg border px-3 py-2",
      }),
      'customer_contact_person': forms.TextInput(attrs={
        "class": "w-full rounded-lg border px-3 py-2",
      }),
      'customer_mobile_no': forms.TextInput(attrs={
        "class": "w-full rounded-lg border px-3 py-2",
      }),
      'customer_business_address': forms.TextInput(attrs={
        "class": "w-full rounded-lg border px-3 py-2",
      }),
      'customer_active': forms.CheckboxInput(attrs={
        "class": "h-4 w-4 rounded border-gray-300",
      }),
    }