from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Restaurant
from django.shortcuts import get_object_or_404
from .forms import RestaurantCreateForm
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
from .forms import SuperUserCreationForm, ClientUserCreationForm
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db import transaction
from .models import Order, OrderItem
from datetime import datetime
from django.views.decorators.cache import never_cache
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils import timezone
from .models import PartnerPayment
from django.contrib.sessions.exceptions import SessionInterrupted
# Create your views here.


from django.shortcuts import render

@login_required(login_url='login')
def home(request):
    restaurants = Restaurant.objects.all()
    return render(request, "home.html", {"restaurants": restaurants})




# View de Login Única (Para todos)
def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Verifica se usuário existe
        if not User.objects.filter(username=username).exists():
            messages.error(request, "Este usuário ainda não possui cadastro.")
            return render(request, "login.html")

        # Tenta autenticar
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("entry_point")
        else:
            messages.error(request, "Senha incorreta.")
    
    return render(request, "login.html")


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

# View de Registro de Gestor
def register_superuser(request):
    form = SuperUserCreationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            # NÃO salva direto no banco, apenas guarda os dados na sessão 
            request.session["pending_superuser"] = {
                "username": form.cleaned_data["username"],
                "password": form.cleaned_data["password"], 
                "email": form.cleaned_data.get("email", "")
            }

            messages.info(request, "Agora crie sua vitrine para concluir o cadastro.")
            return redirect("create_my_store")

    return render(request, "base_app/register_superuser.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('login')
    

def superadmin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Acesso negado")
        return view_func(request, *args, **kwargs)
    return wrapper


@superadmin_required
def admin_platform_dashboard(request):
    restaurants = Restaurant.objects.select_related('owner').all()
    pending_activation_count = restaurants.filter(is_active=False).count()
    pending_payments = PartnerPayment.objects.filter(
        status="pending"
    ).select_related("restaurant__owner", "user").order_by('-created_at')

    context = {
        "restaurants": restaurants,
        "pending_payments": pending_payments,
        "total_restaurants": restaurants.count(),
        "active_restaurants": restaurants.filter(is_active=True).count(),
        "inactive_restaurants": restaurants.filter(is_active=False).count(),
        "pending_payments_count": pending_payments.count(),
        "pending_activation_count": pending_activation_count,
    }

    return render(request, "platform_admin/dashboard_admin.html", context)



@login_required
def payments_list(request):
    if not request.user.is_superuser:
        return redirect("home")

    payments = PartnerPayment.objects.filter(status="pending")

    return render(request,"platform_admin/payments_list.html",{
        "payments": payments
    })


@login_required
def approve_payment(request, payment_id):

    if not request.user.is_superuser:
        return redirect("home")

    payment = get_object_or_404(PartnerPayment,id=payment_id)

    payment.status = "approved"
    payment.save()

    restaurant = payment.restaurant
    restaurant.is_active = True
    restaurant.save()

    user = payment.user
    user.is_active = True
    user.save()

    messages.success(request,"Pagamento aprovado e loja ativada!")

    return redirect("payments_list")


@login_required
def reject_payment(request, payment_id):

    if not request.user.is_superuser:
        return redirect("home")

    payment = get_object_or_404(PartnerPayment,id=payment_id)

    payment.status = "rejected"
    payment.save()

    messages.error(request,"Pagamento recusado")

    return redirect("payments_list")



@login_required
def deactivate_restaurant(request, restaurant_id):

    if not request.user.is_superuser:
        return redirect("home")

    restaurant = get_object_or_404(Restaurant,id=restaurant_id)

    restaurant.is_active = False
    restaurant.save()

    messages.warning(request,"Loja desativada")

    return redirect("platform_dashboard_admin")


@login_required
def activate_restaurant(request, restaurant_id):

    if not request.user.is_superuser:
        return redirect("home")

    restaurant = get_object_or_404(Restaurant,id=restaurant_id)

    restaurant.is_active = True
    restaurant.save()

    messages.success(request,"Loja ativada")

    return redirect("platform_dashboard_admin")

def update_restaurant_status(request, restaurant_id):

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    status = request.POST.get("status")

    if status == "active":
        restaurant.is_active = True
    else:
        restaurant.is_active = False

    restaurant.save()

    return redirect("platform_dashboard_admin")

@login_required
def update_payment_status(request, restaurant_id):

    if not request.user.is_superuser:
        return HttpResponseForbidden("Acesso negado")

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    status = request.POST.get("payment_status")

    restaurant.payment_status = status
    restaurant.save()

    if status == "blocked":
        restaurant.is_active = False
        restaurant.save()

    messages.success(request, "Status de pagamento atualizado!")

    return redirect("platform_dashboard_admin")





@login_required
def store_dashboard(request):

    try:
        profile = StoreProfile.objects.select_related('restaurant').get(user=request.user)
    except StoreProfile.DoesNotExist:
        messages.error(request, "Você não possui uma loja.")
        return redirect("home")

    if profile.role != "OWNER":
        messages.error(request, "Acesso restrito a donos de loja.")
        return redirect("home")

    restaurant = profile.restaurant
    if not restaurant.is_active:
        messages.warning(request, "Sua loja aguarda aprovação do pagamento.")
        return redirect("partner_payment")

    return render(request, "platform/dashboard.html", {"restaurant": restaurant})






@login_required
def partner_payment(request):
    try:
        profile = StoreProfile.objects.select_related('restaurant').get(user=request.user)
    except StoreProfile.DoesNotExist:
        return redirect("home")

    if profile.role != "OWNER":
        return redirect("home")

    restaurant = profile.restaurant
    
    # Se já ativo, vai pro dashboard
    if restaurant.is_active:
        return redirect("store_dashboard")
    
    # Verifica se já tem pagamento pendente
    has_pending_payment = PartnerPayment.objects.filter(
        user=request.user, 
        status="pending"
    ).exists()
    
    context = {
        "restaurant": restaurant,
        "price": 49.00,
        "has_pending_payment": has_pending_payment
    }
    
    return render(request, "payments/payment_page.html", context)



@login_required
def upload_payment_proof(request):
    try:
        profile = StoreProfile.objects.get(user=request.user)
    except StoreProfile.DoesNotExist:
        return redirect("home")

    if profile.role != "OWNER":
        return redirect("home")

    restaurant = profile.restaurant
    
    if request.method == "POST":
        proof = request.FILES.get("proof")
        if not proof:
            messages.error(request, "Selecione um comprovante.")
            return redirect("partner_payment")

        # Impede múltiplos uploads pendentes
        if PartnerPayment.objects.filter(user=request.user, status="pending").exists():
            messages.warning(request, "Você já tem um pagamento pendente.")
            return redirect("partner_payment")

        PartnerPayment.objects.create(
            user=request.user,
            restaurant=restaurant,
            amount=Decimal("49.00"),
            proof=proof,
            status="pending"
        )

        # Logout até aprovação
        logout(request)
        messages.success(request, "✅ Comprovante enviado! Aguarde aprovação do administrador.")
        return redirect("login")

    return redirect("partner_payment")


@login_required
def entry_point(request):
    try:
        profile = StoreProfile.objects.get(user=request.user)
    except StoreProfile.DoesNotExist:
        return redirect("home")

    if profile.role == "ADMIN":
        return redirect("platform_dashboard_admin")
    elif profile.role == "OWNER":
        return redirect("store_dashboard")
    else:
        return redirect("home")



#Removi a autenticação de login porque o usuario está criando a loja, ou seja, não tem como estar logado. O login só acontece depois que o usuário é criado, ou seja, lá no final do processo de criação da loja.
#Outra coisa, a criação do usuário agora acontece dentro de uma transação atômica junto com a criação da loja e do perfil, garantindo que tudo ou nada seja criado. Isso evita ter usuários sem loja ou lojas sem usuário.
####Essa função ainda possui um erro na hora de concluir o cadastro ela não está sendo direcionada para o dashboard da loja, isso acontece porque o login só é feito depois de criar o usuário, e o redirecionamento para o dashboard da loja acontece antes do login, ou seja, ele não reconhece que o usuário acabou de ser criado e logado. Para resolver isso, basta fazer o login do usuário logo após criar a conta, dentro da mesma transação atômica. Assim, quando chegar no redirecionamento para o dashboard da loja, ele já vai reconhecer que o usuário está autenticado e tem uma loja vinculada.



def create_my_store(request):
    pending_user = request.session.get("pending_superuser")


    if not pending_user and not request.user.is_authenticated:
        return redirect("login")
    

    if request.method == "POST":
        form = RestaurantCreateForm(request.POST, request.FILES)

        if form.is_valid():
            try:

                with transaction.atomic():
                    # 1. Criar usuário (se necessário)
                    if pending_user:
                        user = User.objects.create_user(
                            username=pending_user["username"],
                            password=pending_user["password"],
                            email=pending_user["email"]
                        )
                        user.is_staff = False
                        user.is_superuser = False
                        user.is_active = True
                        user.save()

                        # ✅ LOGIN IMEDIATO e salva sessão ANTES de continuar
                        login(request, user)
                        request.session.save()  # ← Força salvar a sessão
                        
                        # Limpa sessão temporária
                        if "pending_superuser" in request.session:
                            del request.session["pending_superuser"]

                    else:
                        user = request.user

                    # 2. Criar restaurante
                    restaurant = form.save(commit=False)
                    restaurant.owner = user
                    restaurant.terms_accepted = True
                    restaurant.terms_accepted_at = timezone.now()  # ← Corrigido o nome do campo
                    restaurant.save()

                    # 3. Criar vínculo
                    StoreProfile.objects.create(
                        user=user,
                        restaurant=restaurant,
                        role="OWNER"
                    )

                # ✅ SESSÃO FINALIZADA com sucesso
                messages.success(request, "Cadastro concluído com sucesso!")
                
                # Força salvar sessão antes do redirect
                request.session.save()
                return redirect("store_dashboard")

            except Exception as e:
                # ✅ TRATAMENTO da exceção SessionInterrupted
                if isinstance(e, SessionInterrupted):
                    messages.error(request, "Sessão expirou. Faça login novamente.")
                    return redirect("login")
                messages.error(request, f"Erro ao finalizar cadastro: {str(e)}")
                return redirect("register_superuser")

    else:
        form = RestaurantCreateForm()

    return render(request, "platform/create_restaurant.html", {"form": form})


def termos_plataforma(request):
    return render(request, "platform/termos.html")


#Funçao sem utlização agora, indeciso se tiro daqui ou se deixo para usar depois
def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Conta ativada com sucesso! Agora você pode fazer login.")
        return redirect("login")
    else:
        messages.error(request, "Link inválido ou expirado.")
        return redirect("home")



@login_required
def dashboard_view(request):
    try:
        profile = StoreProfile.objects.get(user=request.user)
    except StoreProfile.DoesNotExist:
        return redirect("home")

    if profile.role != "OWNER":
        return redirect("home")

    orders = Order.objects.filter(
        restaurant=profile.restaurant
    ).select_related("user")

    context = {
        "restaurant": profile.restaurant,
        "orders": orders
    }

    return render(request, "platform/dashboard.html", context)


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

    form = RestaurantCreateForm(request.POST or None)

    if form.is_valid():
        restaurant = form.save(commit=False)
        restaurant.owner = request.user
        restaurant.save()
        return redirect("platform_dashboard_admin")

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

        return redirect("platform_dashboard_admin")

    return render(request, "platform/create_store_admin.html", {
        "form": form
    })



def get_store_restaurant(user):
    try:
        profile = StoreProfile.objects.get(user=user)  # ✅ Busca direta
        # ou
        # profile = getattr(user, 'storeprofile', None)  # ✅ lowercase
    except (StoreProfile.DoesNotExist, AttributeError):
        raise PermissionDenied("Usuário não possui loja")

    if profile.role not in ["OWNER", "STAFF"]:
        raise PermissionDenied("Sem permissão para acessar esta loja")

    return profile.restaurant



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
            "img": item.image.url if item.image else "",
            "restaurant_id": item.restaurant.id
        }
        messages.success(request, f"{item.name} adicionado ao carrinho.")

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("restaurant_home", slug=item.restaurant.slug)




def cart_detail(request):

    cart = request.session.get("cart", {})

    # pega pagamento se vier do form
    pagamento = request.POST.get("pagamento") or request.GET.get("pagamento") or "Não informado"

    total = 0
    items_for_template = []
    restaurant_whatsapp = ""

    # 1️⃣ Processa os itens do carrinho
    for key, item in cart.items():

        if isinstance(item, dict):
            price = float(item.get("price", 0))
            quantity = int(item.get("quantity", 0))
            subtotal = price * quantity

            items_for_template.append({
                "id": key,
                "name": item.get("name", ""),
                "price": price,
                "quantity": quantity,
                "subtotal": subtotal,
                "restaurant_id": item.get("restaurant_id"),
            })

            total += subtotal

    # 2️⃣ Busca WhatsApp do restaurante
    if items_for_template:
        res_id = items_for_template[0].get("restaurant_id")

        try:
            res = Restaurant.objects.get(id=res_id)

            num_limpo = "".join(filter(str.isdigit, str(res.whatsapp)))
            restaurant_whatsapp = (
                f"55{num_limpo}" if not num_limpo.startswith("55") else num_limpo
            )

        except Restaurant.DoesNotExist:
            restaurant_whatsapp = ""

    # 3️⃣ Dados do cliente
    cliente_nome = request.user.get_full_name() or request.user.username

    try:
        perfil = StoreProfile.objects.get(user=request.user)
        cliente_endereco = getattr(
            perfil,
            "address",
            "📍 Informar endereço no WhatsApp"
        )
    except StoreProfile.DoesNotExist:
        cliente_endereco = "📍 Informar endereço no WhatsApp"

    # 4️⃣ Montagem da mensagem
    whatsapp_text = "🍔 *NOVO PEDIDO - COMAÍ*\n"
    whatsapp_text += "━━━━━━━━━━━━━━━━━━━━\n\n"

    whatsapp_text += "👤 *DADOS DO CLIENTE*\n"
    whatsapp_text += f"👤 *Cliente:* {cliente_nome}\n"
    whatsapp_text += f"🕒 *Data:* {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"

    whatsapp_text += "🧾 *ITENS DO PEDIDO*\n"
    whatsapp_text += "━━━━━━━━━━━━━━━━━━━━\n"

    for item in items_for_template:
        whatsapp_text += f"✅ {item['quantity']}x {item['name']}\n"
        whatsapp_text += f"   💰 R$ {item['subtotal']:.2f}\n"

    whatsapp_text += "\n━━━━━━━━━━━━━━━━━━━━\n"
    whatsapp_text += f"💵 *VALOR TOTAL DO PEDIDO*\n"
    whatsapp_text += f"R$ {total:.2f}\n\n"

    whatsapp_text += "💳 *FORMA DE PAGAMENTO*\n"
    whatsapp_text += f"💳 *Pagamento:* {pagamento}\n\n"

    whatsapp_text += "📍 *ENDEREÇO DE ENTREGA*\n"
    whatsapp_text += f"{cliente_endereco}\n\n"

    whatsapp_text += "Poderiam confirmar o pedido e informar o tempo de entrega?"

    # 5️⃣ Link WhatsApp
    whatsapp_link = ""

    if restaurant_whatsapp:
        whatsapp_link = f"https://wa.me/{restaurant_whatsapp}?text={quote(whatsapp_text)}"

    context = {
        "cart": items_for_template,
        "total": total,
        "whatsapp_url": whatsapp_link,
        "restaurant_whatsapp": restaurant_whatsapp,
        "pagamento": pagamento,
    }

    return render(request, "cart_detail.html", context)


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




####Trabalhar nessa parte pra quando finalizar o pedido por whatsApp o carrinho esvaziar
#### order Quem é o cabeça dessaa função
@login_required
@never_cache
def create_order(request):
    """
    Cria um pedido a partir do carrinho da sessão e limpa o carrinho imediatamente.
    """
    cart = request.session.get("cart")

    if not cart:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect("home")

    try:
        # Descobre o restaurante pelo primeiro item do carrinho
        first_item_id = next(iter(cart))
        first_product = get_object_or_404(Product, id=first_item_id)
        restaurant = first_product.restaurant


        with transaction.atomic():
            # Cria o pedido principal
            order = Order.objects.create(
                restaurant=restaurant,
                user=request.user,
                status="pending",
                total_price=Decimal("0.00")
            )

            current_total = Decimal("0.00")

            # Cria os itens do pedido
            for item_id, item in cart.items():
                product = get_object_or_404(Product, id=item_id)
                quantity = int(item.get("quantity", 1))
                price = Decimal(str(item.get("price")))

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
                current_total += (price * quantity)

            # Atualiza o total final
            order.total_price = current_total
            order.save()

            # --- LIMPEZA AGRESSIVA DA SESSÃO ---
            if 'cart' in request.session:
                del request.session["cart"]
            
            request.session.modified = True
            request.session.save() # Força gravar no banco de sessões antes do redirect

        messages.success(request, "Pedido realizado com sucesso!")
        return redirect("order_success/order_sucess.html", order_id=order.id)

    except Exception as e:
        messages.error(request, f"Erro ao processar pedido: {str(e)}")
        #Provavelmente eu terei que remover esse order succes.html por conta que o Redirect usa nome da URL, não template.
        return redirect("orders/order_sucess.html")


@login_required
@never_cache
def order_success(request, order_id):
    # Busca o pedido que acabou de ser criado
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # 1. Busca o WhatsApp do restaurante vinculado ao pedido
    restaurant = order.restaurant
    num_limpo = ''.join(filter(str.isdigit, str(restaurant.whatsapp)))
    restaurant_whatsapp = f"55{num_limpo}" if not num_limpo.startswith('55') else num_limpo

    # 2. Dados do Cliente
    cliente_nome = request.user.get_full_name() or request.user.username
    
    # Tenta buscar o endereço no StoreProfile
    try:
        perfil = StoreProfile.objects.get(user=request.user)
        cliente_endereco = getattr(perfil, 'address', "📍 _Endereço não informado_")
    except StoreProfile.DoesNotExist:
        cliente_endereco = "📍 _Endereço não informado_"

    # 3. Montagem do Ticket Profissional baseado no BANCO DE DADOS (mais seguro)
    whatsapp_text = f"📌 *SOLICITAÇÃO DE PEDIDO #{order.id}*\n"
    whatsapp_text += f"_{datetime.now().strftime('%d/%m/%Y às %H:%M')}_\n"
    whatsapp_text += f"------------------------------------------\n\n"
    
    whatsapp_text += f"*DADOS DO CLIENTE*\n"
    whatsapp_text += f"👤 {cliente_nome.upper()}\n"
    whatsapp_text += f"🏠 {cliente_endereco}\n\n"
    
    whatsapp_text += f"*RESUMO DOS ITENS*\n"
    
    for item in order.items.all(): # Usando o related_name do seu model OrderItem
        whatsapp_text += f"▪️ {item.quantity}x {item.product.name}\n"
        whatsapp_text += f"  (R$ {item.get_subtotal():.2f})\n"
    
    whatsapp_text += f"\n*VALOR TOTAL: R$ {order.total_price:.2f}*\n"
    whatsapp_text += f"------------------------------------------\n\n"
    whatsapp_text += "Olá! Acabei de realizar meu pedido no site. Segue o comprovante para confirmação."

    whatsapp_url = f"https://wa.me/{restaurant_whatsapp}?text={quote(whatsapp_text)}"


     
    return render(request, "orders/order_success.html", {
        "order": order, 
        "total": order.total_price,
        "whatsapp_url": whatsapp_url # Enviamos o link pronto para o template
    })