from django.db import models
from django.contrib.auth.models import User
from django.conf import settings





# Create your models here.


class Restaurant(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    whatsapp = models.CharField(max_length=20, help_text= "Apenas números com DDD (ex:11999998888)")
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="restaurants"
    )

    # NOVOS CAMPOS DE IMAGEM
    logo = models.ImageField(
        upload_to="restaurants/logos/",
        blank=True,
        null=True
    )

    banner = models.ImageField(
        upload_to="restaurants/banners/",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=False)
    
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    PAYMENT_STATUS = [
    ("paid", "Em dia"),
    ("pending", "Pendente"),
    ("late", "Atrasado"),
    ("blocked", "Bloqueado"),
    ]

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="pending"
        )

    def __str__(self):
        return self.name


class PartnerPayment(models.Model):

    STATUS = (
        ("pending", "Pendente"),
        ("approved", "Aprovado"),
        ("rejected", "Recusado"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    proof = models.ImageField(upload_to="payments/")

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        # Se pagamento aprovado ativa usuário e restaurante
        if self.status == "approved":

            self.user.is_active = True
            self.user.save()

            self.restaurant.is_active = True
            self.restaurant.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - R${self.amount}"
    

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

####Parte de divisão de perfis de loja e usuários####
class StoreProfile(models.Model):
    ROLE_CHOICES = (
        ("OWNER", "Dono da Loja"),
        ("STAFF", "Funcionário"),
        ("CLIENT", "Cliente"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="STAFF"
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Category(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="categories"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

####ESSA PARTE ESTÁ DUPLICADA, COM A CLASS PRODUCT. DELETAR ESSA CLAS ITEM MAS FUTURAMENTE####
class Item(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="items"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="items"
    )
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to="items/", blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="products"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    
    image = models.ImageField(
        upload_to="products/", 
        blank=True, 
        null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pendente"),
        ("confirmed", "Confirmado"),
        ("cancelled", "Cancelado"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.restaurant.name}"

    class Meta:
        ordering = ["-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def get_subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.quantity}x)"
