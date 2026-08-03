from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "product_code",
            "product_name",
            "factory_price",
            "shelf_life",
            "product_packaging",
            "discontinued",
        ]

        widgets = {
            "product_code": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-gray-300 px-4 py-2",
            }),
            "product_name": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-gray-300 px-4 py-2",
            }),
            "factory_price": forms.NumberInput(attrs={
                "class": "w-full rounded-lg border border-gray-300 px-4 py-2",
                "step": "0.01",
            }),
            "shelf_life": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-gray-300 px-4 py-2",
            }),
            "product_packaging": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-gray-300 px-4 py-2",
            }),
            "discontinued": forms.CheckboxInput(attrs={
                "class": "h-4 w-4 rounded border-gray-300",
            }),
        }