from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from logindata.models import Product


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']
