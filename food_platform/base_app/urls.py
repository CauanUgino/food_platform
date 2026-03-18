from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views import (
    home,
    custom_login,
    restaurant_home,
    store_dashboard,
    admin_platform_dashboard,
    create_restaurant,
    create_store_admin,
    store_dashboard,
    category_list,
    category_create,
    category_edit,
    category_delete,
    product_list,
    product_create,
    product_edit,
    product_delete,
    cart_detail,
    add_to_cart,
    termos_plataforma,    
)

urlpatterns = [
    path("", home, name="home"),
    path("r/<slug:slug>/", restaurant_home, name="restaurant_home"),
    path("login/", custom_login, name="login"),

    # 🔽 REGISTROS 
    path('register/cliente/', views.register_user, name='register_user'),
    path('register/gestor/', views.register_superuser, name='register_superuser'),
    path('logout/', LogoutView.as_view(template_name='login.html'), name='logout'),

    # Confirmação de Email
    path("confirmar-email/<uidb64>/<token>/", views.confirm_email, name="confirm_email"),

    # 🔹 ENTRY POINT
    path("entrar/", views.entry_point, name="entry_point"),

    # 🔽 PAINEL DO PARCEIRO (Dono do Restaurante)
    path('painel/', store_dashboard, name='store_dashboard'),
    path("pagamento/", views.partner_payment, name="partner_payment"),
    path("pagamento/enviar/", views.upload_payment_proof, name="upload_payment_proof"),
    path("minha-vitrine/criar/", views.create_my_store, name="create_my_store"),
    
    # 🔽 GESTÃO COMAÍ (Administração do Superusuário)
    path('admin-comaí/', admin_platform_dashboard, name='platform_dashboard_admin'),
    path("platform/restaurants/new/", create_restaurant, name="create_restaurant"),
    path("platform/store-admin/new/", create_store_admin, name="create_store_admin"),
    path("platform/payments/", views.payments_list, name="payments_list"),
    path("platform/payment/<int:payment_id>/approve/", views.approve_payment, name="approve_payment"),
    path("platform/payment/<int:payment_id>/reject/", views.reject_payment, name="reject_payment"),
    path("platform/restaurant/<int:restaurant_id>/deactivate/", views.deactivate_restaurant, name="deactivate_restaurant"),
    path("platform/restaurant/<int:restaurant_id>/activate/", views.activate_restaurant, name="activate_restaurant"),

    # 🔽 STATUS E TERMOS
    path("termos/", termos_plataforma, name="termos"),
    path("restaurant/<int:restaurant_id>/status/", views.update_restaurant_status, name="update_restaurant_status"),
    path("restaurant/<int:restaurant_id>/payment-status/", views.update_payment_status, name="update_payment_status"),
    path('dashboard/', views.dashboard_view, name='dashboard'), # Mantida conforme pedido

    # 🔽 CATEGORIES
    path("store/categories/", category_list, name="category_list"),
    path("store/categories/new/", category_create, name="category_create"),
    path("store/categories/<int:pk>/edit/", category_edit, name="category_edit"),
    path("store/categories/<int:pk>/delete/", category_delete, name="category_delete"),

    # 🔽 PRODUCTS
    path("store/products/", product_list, name="product_list"),
    path("store/products/new/", product_create, name="product_create"),
    path("store/products/<int:pk>/edit/", product_edit, name="product_edit"),
    path("store/products/<int:pk>/delete/", product_delete, name="product_delete"),

    # 🔽 CART
    path("cart/", cart_detail, name="cart_detail"),
    path('add-to-cart/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),

    # 🔽 ORDER
    path("pedido/criar/", views.create_order, name="create_order"),
    path("pedido/sucesso/<int:order_id>/", views.order_success, name="order_success"),
]