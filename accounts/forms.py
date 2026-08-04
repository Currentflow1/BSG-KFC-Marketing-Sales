from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission
from django import forms
from .models import CustomUser

class AccountCreateForm(UserCreationForm):
    email = forms.EmailField()
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)

    class Meta:
        model = CustomUser
        fields = [
            "username", 
            "email", 
            "password1", 
            "password2", 
            "groups",
            ]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-gray-300 px-4 py-2",
            }), 
            "email": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-gray-300 px-4 py-2",
            }), 
            "password1": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-gray-300 px-4 py-2",
            }), 
            "password2": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-gray-300 px-4 py-2",
            }), 
            "groups":forms.Select(attrs={
                "class": "w-50 rounded-lg border border-gray-300 px-4 py-2",
            }),
        }


class GroupCreateForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), required=False)

    class Meta:
        model = Group
        fields = [
            "name", 
            "permissions",
          ]


        widgets = {
            'name': forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-gray-300 px-4 py-2",
            }),
            'permissions': forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-gray-300 px-4 py-2",
            }),
        }