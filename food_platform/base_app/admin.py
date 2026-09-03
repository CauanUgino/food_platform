from django.contrib import admin
from .models import PartnerPayment
from .models import (
    Restaurant,
    StoreProfile,
    Category,
    Item,
    Product,
    Order,
    OrderItem
)

##Essa classe é responsável por registrar o modelo Restaurant no painel de administração do Django, permitindo que os administradores gerenciem restaurantes, incluindo informações como nome, proprietário, contato e imagens. Além disso, ela fornece funcionalidades de pesquisa e filtragem para facilitar a administração dos restaurantes cadastrados.
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "owner",
        "whatsapp",
        "created_at"
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    search_fields = (
        "name",
        "whatsapp"
    )

    list_filter = (
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )

    fieldsets = (

        ("Informações do Restaurante", {
            "fields": (
                "name",
                "slug",
                "description",
                "owner",
            )
        }),

        ("Contato", {
            "fields": (
                "whatsapp",
            )
        }),

        ("Imagens do Restaurante", {
            "fields": (
                "logo",
                "cover",
            )
        }),

        ("Sistema", {
            "fields": (
                "created_at",
            )
        }),
    )

##Essa classe é responsável por registrar o modelo StoreProfile no painel de administração do Django, permitindo que os administradores gerenciem perfis de loja, incluindo informações como usuário, restaurante e função.
@admin.register(StoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "restaurant", "role")



##Essa classe é responsável por registrar o modelo PartnerPayment no painel de administração do Django, permitindo que os administradores gerenciem pagamentos de parceiros, incluindo informações como usuário, restaurante, valor e status.
@admin.register(PartnerPayment)
class PartnerPaymentAdmin(admin.ModelAdmin):

    list_display = ("user", "restaurant", "amount", "status", "created_at")

    actions = ["approve_payment"]

    def approve_payment(self, request, queryset):

        for payment in queryset:

            payment.status = "approved"
            payment.save()

            restaurant = payment.restaurant
            restaurant.is_active = True
            restaurant.save()

##Essa classe é responsável por registrar o modelo Category no painel de administração do Django, permitindo que os administradores gerenciem categorias de produtos, incluindo informações como nome e restaurante associado.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant")

##Essa classe é responsável por registrar o modelo Item no painel de administração do Django, permitindo que os administradores gerenciem itens de produtos, incluindo informações como nome, restaurante associado, preço e disponibilidade.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "price", "is_available")

##Essa classe é responsável por registrar o modelo Product no painel de administração do Django, permitindo que os administradores gerenciem produtos, incluindo informações como nome, restaurante associado, categoria, preço e disponibilidade.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "category", "price", "available")
    list_filter = ("restaurant", "available")


##Essa classe é responsável por registrar o modelo OrderItem no painel de administração do Django, permitindo que os administradores gerenciem itens de pedidos, incluindo informações como pedido associado, produto, quantidade e preço.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

##Essa classe é responsável por registrar o modelo Order no painel de administração do Django, permitindo que os administradores gerenciem pedidos, incluindo informações como restaurante associado, usuário, status, preço total e data de criação. Além disso, ela exibe os itens do pedido como uma lista inline para facilitar a visualização e edição.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurant", "user", "status", "total_price", "created_at")
    list_filter = ("status", "restaurant")
    inlines = [OrderItemInline]
