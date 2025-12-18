from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from .models import StoreProfile

def get_store_restaurant(user):
    if not hasattr(user, "storeprofile"):
        raise PermissionDenied("Usuário não é admin de loja")

    return user.storeprofile.restaurant
