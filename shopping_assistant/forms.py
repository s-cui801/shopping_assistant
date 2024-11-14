from django import forms
from .models import Customers  # assuming your customers model is named Customers

class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Customers
        fields = ['first_name', 'last_name', 'username', 'password']