from django import forms
from .models import Restaurant
from django.contrib.auth.models import User
from .models import StoreProfile, Restaurant
from .models import Category, Product
from django import forms
from .models import Item
from django import forms
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy

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
    
    

class RestaurantCreateForm(forms.ModelForm):
    
       

    class Meta:
        model = Restaurant
        fields = [
            "name",
            "slug",
            "whatsapp",
            "description",
            "logo",
            "banner",
            
        ]

        # Placeholders e aparência dos campos
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Ex: Pizzaria do Vale"
            }),

            "slug": forms.TextInput(attrs={
                "placeholder": "pizzaria-do-vale"
            }),

            "whatsapp": forms.TextInput(attrs={
                "placeholder": "(00) 00000-0000"
            }),

            "description": forms.Textarea(attrs={
                "placeholder": "Ex: A melhor massa artesanal da região. Atendemos todos os dias com ingredientes frescos e selecionados.",
                "rows": 4
            }),

            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            
            'banner': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

        # Nome que aparece na tela
        labels = {
            "name": "Nome da vitrine",
            "slug": "URL da vitrine",
            "whatsapp": "WhatsApp para pedidos",
            "description": "Descrição",
            "logo": "Logo do restaurante",
            "banner": "Imagem de capa do restaurante",
        }

        # Texto de ajuda abaixo do campo
        help_texts = {
            "slug": "Sua vitrine será acessada por este nome na URL.",
        }

    # ✅ FORA do Meta (CORRETO)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['logo'].required = False
        self.fields['banner'].required = False


           
        

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