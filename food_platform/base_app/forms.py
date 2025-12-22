from django import forms
from .models import Restaurant
from django.contrib.auth.models import User
from .models import StoreProfile, Restaurant
from .models import Category, Product
from django import forms
from .models import Item
from django import forms


# Adicione esta classe ao seu forms.py
# Form para Clientes
class ClientUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user

# Form para Gestores
class SuperUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user
    
    
class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ["name", "slug", "description"]

class StoreAdminCreationForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    restaurant = forms.ModelChoiceField(
        queryset=Restaurant.objects.all()
    )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["category", "name", "description", "price", "available"]

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["category", "name", "price", "is_available"]