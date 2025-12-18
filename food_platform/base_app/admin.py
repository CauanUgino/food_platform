from django.contrib import admin
from .models import Restaurant, StoreProfile, Category, Item


# Register your models here.


admin.site.register(Restaurant)
admin.site.register(StoreProfile)
admin.site.register(Category)
admin.site.register(Item)
