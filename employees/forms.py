from django import forms
from .models import Employee

FIELD_CLASS = "w-full rounded-lg border px-4 py-2"
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "employee_name",
            "employee_nickname",
            "employee_group",
            "employee_position",
            "employee_birthdate",
            "employee_hiredate",
            "employee_sex",
            "employee_sss",
            "employee_gsis",
            "employeeActive",
        ]

        widgets = {
            "employee_name": forms.TextInput(attrs={
                "class": FIELD_CLASS,
            }),
            "employee_nickname": forms.TextInput(attrs={
                "class": FIELD_CLASS,
            }),
            "employee_group": forms.TextInput(attrs={
                "class": FIELD_CLASS,
            }),
            "employee_position": forms.TextInput(attrs={
                "class": FIELD_CLASS,
            }),
            "employee_birthdate": forms.DateInput(attrs={
                "class": FIELD_CLASS,
                "type": "date",
            }),
            "employee_hiredate": forms.DateInput(attrs={
                "class": FIELD_CLASS,
                "type": "date",
            }),
            "employee_sex": forms.Select(attrs={
                "class": FIELD_CLASS,
            }),
            "employee_sss": forms.TextInput(attrs={
                "class": FIELD_CLASS,
            }),
            "employee_gsis": forms.TextInput(attrs={
                "class": FIELD_CLASS,
            }),
            "employeeActive": forms.CheckboxInput(attrs={
                "class": "h-4 w-4 rounded border-gray-300",
            }),
        }