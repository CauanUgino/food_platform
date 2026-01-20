from django.contrib import admin
from .models import (
    Restaurant,
    StoreProfile,
    Category,
    Item,
    Product,
    Order,
    OrderItem
)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(StoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "restaurant", "role")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant")

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "price", "is_available")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "category", "price", "available")
    list_filter = ("restaurant", "available")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurant", "user", "status", "total_price", "created_at")
    list_filter = ("status", "restaurant")
    inlines = [OrderItemInline]
