from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Restaurant
from django.shortcuts import get_object_or_404
from .forms import RestaurantForm
from django.contrib.auth.models import User
from .models import StoreProfile
from .forms import StoreAdminCreationForm
from .forms import CategoryForm
from .models import Category 
from .models import Item
from .forms import ItemForm
from django.core.exceptions import PermissionDenied
from .models import Product
from decimal import Decimal
from urllib.parse import quote
# Correto
from .models import Product
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import SuperUserCreationForm
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.contrib import messages

# Create your views here.


from django.shortcuts import render

@login_required(login_url='login')
def home(request):
    restaurants = Restaurant.objects.all()
    return render(request, "home.html", {"restaurants": restaurants})




def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Usuário ou senha incorretos")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('login')

def register_superuser(request):
    if request.method == 'POST':
        form = SuperUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Superusuário criado com sucesso!')
            return redirect('login')
    else:
        form = SuperUserCreationForm()
    return render(request, 'register_superuser.html', {'form': form})

@login_required
def platform_dashboard(request):
    if not request.user.is_superuser:
        return redirect("home")

    restaurants = Restaurant.objects.all()
    return render(request, "platform/dashboard.html", {
        "restaurants": restaurants
    })


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}!')
            return redirect('login') # Certifique-se que o nome da sua URL de login é 'login'
    else:
        form = UserCreationForm()
    return render(request, 'base_app/register.html', {'form': form})

@login_required
def store_dashboard(request):
    # Verifica se o usuário é superusuário
    if request.user.is_superuser:
        return redirect("platform_dashboard")

    profile = StoreProfile.objects.get(user=request.user)
    restaurant = profile.restaurant

    context = {
        "restaurant": restaurant,
        "total_categories": restaurant.categories.count(),
        "total_items": restaurant.items.count(),
        "public_url": request.build_absolute_uri(
            f"/restaurant/{restaurant.slug}/"
        )
    }

    return render(request, "platform/dashboard.html", context)

def dashboard_view(request):
    # Aqui pegamos os dados para exibir nos cards de métricas
    context = {
        'total_categories': Category.objects.count(),
        'total_items': Product.objects.count(),
    }
    return render(request, 'dashboard.html', context)

def restaurant_home(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)

    categories = restaurant.categories.prefetch_related(
        "products"

    )   

    return render(request, "public/restaurant_home.html", {
        "restaurant": restaurant,
        "categories": categories,
         
    })

@login_required
def create_restaurant(request):
    if not request.user.is_superuser:
        return redirect("home")

    form = RestaurantForm(request.POST or None)

    if form.is_valid():
        restaurant = form.save(commit=False)
        restaurant.owner = request.user
        restaurant.save()
        return redirect("platform_dashboard")

    return render(request, "platform/create_restaurant.html", {
        "form": form
    })

@login_required
def create_store_admin(request):
    if not request.user.is_superuser:
        return redirect("home")

    form = StoreAdminCreationForm(request.POST or None)

    if form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"]
        )

        StoreProfile.objects.create(
            user=user,
            restaurant=form.cleaned_data["restaurant"]
        )

        return redirect("platform_dashboard")

    return render(request, "platform/create_store_admin.html", {
        "form": form
    })

def get_store_restaurant(user):
    if not hasattr(user, "storeprofile"):
        raise PermissionDenied
    return user.storeprofile.restaurant


@login_required
def category_list(request):
    profile = StoreProfile.objects.get(user=request.user)
    categories = Category.objects.filter(
        restaurant=profile.restaurant
    )

    return render(request, "store/category_list.html", {
        "categories": categories
    })


@login_required
def category_create(request):
    restaurant = get_store_restaurant(request.user)

    if request.method == "POST":
        name = request.POST.get("name")
        Category.objects.create(
            name=name,
            restaurant=restaurant
        )
        return redirect("category_list")

    return render(request, "store/category_form.html")


@login_required
def category_edit(request, pk):
    restaurant = get_store_restaurant(request.user)
    category = get_object_or_404(Category, pk=pk, restaurant=restaurant)

    if request.method == "POST":
        category.name = request.POST.get("name")
        category.save()
        return redirect("category_list")

    return render(request, "store/category_form.html", {
        "category": category
    })

@login_required
def category_delete(request, pk):
    restaurant = get_store_restaurant(request.user)
    category = get_object_or_404(Category, pk=pk, restaurant=restaurant)

    if request.method == "POST":
        category.delete()
        return redirect("category_list")

    return render(request, "store/category_confirm_delete.html", {
        "category": category
    })


@login_required
def product_list(request):
    restaurant = get_store_restaurant(request.user)

    products = Product.objects.filter(
        restaurant=restaurant
    ).select_related("category")

    return render(request, "store/products/list.html", {
        "products": products
    })


@login_required
def product_create(request):
    restaurant = get_store_restaurant(request.user)

    categories = Category.objects.filter(
        restaurant=restaurant
    )

    if request.method == "POST":
        Product.objects.create(
            restaurant=restaurant,
            category_id=request.POST["category"],
            name=request.POST["name"],
            description=request.POST.get("description", ""),
            price=request.POST["price"],
        )
        return redirect("product_list")

    return render(request, "store/products/create.html", {
        "categories": categories
    })


@login_required
def product_edit(request, pk):
    restaurant = get_store_restaurant(request.user)
    # Buscamos o Product (e garantimos que pertence ao restaurante do usuário)
    product = get_object_or_404(Product, pk=pk, restaurant=restaurant)
    
    categories = Category.objects.filter(restaurant=restaurant)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
        product.price = request.POST.get("price")
        product.category_id = request.POST.get("category")
        product.save()
        messages.success(request, "Produto atualizado com sucesso!")
        return redirect("product_list")

    return render(request, "store/products/create.html", { # Reaproveitamos o template de criar
        "product": product,
        "categories": categories
    })

@login_required
def product_delete(request, pk):
    restaurant = get_store_restaurant(request.user)
    product = get_object_or_404(Product, pk=pk, restaurant=restaurant)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Produto excluído com sucesso!")
        return redirect("product_list")

    return render(request, "store/products/confirm_delete.html", {
        "product": product
        
    })
    





@require_POST
def add_to_cart(request, item_id):
    item = get_object_or_404(Product, id=item_id)

    cart = request.session.get("cart", {})

    item_id_str = str(item.id)

    if item_id_str in cart:
        cart[item_id_str]["quantity"] += 1
        messages.success(request, f"Mais um {item.name} adicionado ao carrinho.")

    else:
        cart[item_id_str] = {
            "name": item.name,
            "price": float(item.price),
            "quantity": 1,
            "img": item.image.url if item.image else ""
        }
        messages.success(request, f"{item.name} adicionado ao carrinho.")

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("restaurant_home", slug=item.restaurant.slug)

    
def cart_detail(request):
    # 1. Pega o carrinho da sessão
    cart = request.session.get("cart", {})
    
    total = 0
    items_for_template = []

    # 2. Processa os itens com segurança
    for key, item in cart.items():
        # Verificamos se o item é realmente um dicionário para evitar o erro de 'int'
        if isinstance(item, dict):
            price = float(item.get('price', 0))
            quantity = int(item.get('quantity', 0))
            subtotal = price * quantity

            # Adicionamos ao contexto que vai para o HTML
            items_for_template.append({
                'id': key,
                'name': item.get('name', ''),
                'price': price,
                'quantity': quantity,
                'subtotal': subtotal
            })
            
            total += subtotal
            
    # 3. Monta a mensagem para WhatsApp
    whatsapp_text = "Olá! Gostaria de fazer o pedido:\n"
    for item in items_for_template:
        whatsapp_text += f"- {item['name']} x {item['quantity']} = R$ {item['subtotal']:.2f}\n"
    whatsapp_text += f"\n*Total: R$ {total:.2f}*"

    # 4. Link do WhatsApp com encoding correto
    whatsapp_link = f"https://wa.me/SEU_NUMERO_AQUI?text={quote(whatsapp_text)}"

    return render(request, "cart_detail.html", {
        "cart": items_for_template,
        "total": total,
        "whatsapp_url": whatsapp_link
    })

def remove_from_cart(request, item_id):
    cart = request.session.get("cart", {})
    item_id_str = str(item_id)

    if item_id_str in cart:
        del cart[item_id_str]
        request.session["cart"] = cart
        request.session.modified = True
        messages.success(request, "Produto removido do carrinho.")
    
    return redirect("cart_detail")

def clear_cart(request):
    if "cart" in request.session:
        del request.session["cart"]
        request.session.modified = True
        messages.success(request, "O carrinho foi esvaziado.")
    
    return redirect("cart_detail")