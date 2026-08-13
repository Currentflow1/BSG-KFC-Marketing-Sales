from django import forms
from .models import Area, AreaPrice

FIELD_CLASS_SELECT = "w-50 rounded-lg border px-3 py-2"
FIELD_CLASS_ALL = "w-full rounded-lg border px-3 py-2"

class AreaForm(forms.ModelForm):
  class Meta: 
    model = Area
    fields = ['area_name']

    widgets = {
      'area_name': forms.TextInput(attrs={
        "class": FIELD_CLASS_ALL
      }),
    }


class AreaPriceForm(forms.ModelForm):
  class Meta:
    model = AreaPrice
    fields = [
      'area_name',
      'product_name',
      'area_price',
    ]

    widgets = {
      'area_name': forms.Select(attrs={
        "class": FIELD_CLASS_SELECT
      }),
      'product_name': forms.Select(attrs={
        "class": FIELD_CLASS_SELECT
      }),
      'area_price': forms.NumberInput(attrs={
        "class": FIELD_CLASS_ALL
      }),
    }