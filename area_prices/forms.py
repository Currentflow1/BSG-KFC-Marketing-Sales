from django import forms
from .models import Area, Area_price

class AreaForm(forms.ModelForm):
  class Meta: 
    model = Area
    fields = [
      'area_name',
    ]

    widgets = {
      'area_name': forms.TextInput(attrs={
        "class": "w-full rounded-lg border px-3 py-2",
      }),
    }


class AreaPriceForm(forms.ModelForm):
  class Meta:
    model: Area_price
    fields = [
      'area_name',
      'product_name',
      'area_price',
    ]

    widgets = {
      'area_name': forms.Select(attrs={
        "class": "w-50 rounded-lg border px-3 py-2",
      }),
      'product_name': forms.Select(attrs={
        "class": "w-50 rounded-lg border px-3 py-2",
      }),
      'area_price': forms.NumberInput(attrs={
        "class": "w-full rounded-lg border px-3 py-2",
      }),
    }