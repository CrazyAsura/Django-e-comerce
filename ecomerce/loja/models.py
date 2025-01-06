from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from decimal import Decimal

class AuthorizationManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Authorization(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    read = models.BooleanField(default=False)
    insert = models.BooleanField(default=False)
    update = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)

    objects = AuthorizationManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'administrator')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(models.Model):
    USER_TYPES = [
        ('customer', 'Customer'),
        ('administrator', 'Administrator'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    birth_date = models.DateField()
    cpf = models.CharField(max_length=14, unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    authorization = models.ManyToManyField(Authorization, related_name='users', blank=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='store_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='store_user_permissions',
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'birth_date', 'cpf']

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.birth_date and self.birth_date > timezone.now().date():
            raise ValidationError('Birth date cannot be in the future.')

class Address(models.Model):
    STATES = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'),
        ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
        ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'),
        ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'),
        ('SE', 'Sergipe'), ('TO', 'Tocantins'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    residence_number = models.CharField(max_length=10)
    zip_code = models.CharField(max_length=9)
    street = models.CharField(max_length=200)
    complement = models.CharField(max_length=100, blank=True, null=True)
    neighborhood = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, choices=STATES)

    def __str__(self):
        return f'{self.street}, {self.residence_number} - {self.neighborhood}, {self.city} - {self.state}'

    def clean(self):
        super().clean()
        if len(self.zip_code.replace('-', '')) != 8:
            raise ValidationError('Invalid ZIP code. Must contain 8 digits.')

class Phone(models.Model):
    PHONE_TYPES = [
        ('mobile', 'Mobile'),
        ('home', 'Home'),
        ('work', 'Work'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phones')
    number = models.CharField(max_length=20)
    ddd = models.CharField(max_length=3)
    type = models.CharField(max_length=11, choices=PHONE_TYPES)

    def __str__(self):
        return f'{self.get_type_display()}: {self.number}'

    def clean(self):
        super().clean()
        clean_number = ''.join(filter(str.isdigit, self.number))
        if len(clean_number) < 10 or len(clean_number) > 11:
            raise ValidationError('Invalid phone number.')

class Category(models.Model):
    image = models.ImageField(upload_to='categories/')
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    discount = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    width = models.DecimalField(max_digits=10, decimal_places=2, help_text="Product width in centimeters", validators=[MinValueValidator(0)])
    length = models.DecimalField(max_digits=10, decimal_places=2, help_text="Product length in centimeters", validators=[MinValueValidator(0)])
    height = models.DecimalField(max_digits=10, decimal_places=2, help_text="Product height in centimeters", validators=[MinValueValidator(0)])
    weight = models.DecimalField(max_digits=10, decimal_places=3, help_text="Product weight in kilograms", validators=[MinValueValidator(0)])
    color = models.CharField(max_length=30)
    materials = models.CharField(max_length=255, help_text="Product materials, separated by comma")
    fragilities = models.TextField(help_text="Product fragilities, if any", blank=True, null=True)
    customer_risk = models.TextField(help_text="Possible risks to customer", blank=True, null=True)

    def __str__(self):
        return self.name

    def price_with_discount(self):
        return Decimal(self.price * (1 - self.discount / 100) )
    
    def price_without_discount(self):
        return self.price

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    expiration_date = models.DateTimeField()
    
    def __str__(self):
        return self.code

    def is_valid(self):
        return timezone.now() <= self.expiration_date
    
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.unit_price

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='delivery_orders')
    total_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    cashback = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Order {self.id} - {self.user.name}'

    def update_total_value(self):
        subtotal = sum(item.subtotal() for item in self.items.all())
        
        if self.coupon and self.coupon.is_valid():
            discount = subtotal * (self.coupon.discount / 100)
            self.total_value = subtotal - discount
        else:
            self.total_value = subtotal

        self.cashback = self.total_value * Decimal('0.05')  # 5% cashback
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.quantity}x {self.product.name} - Order {self.order.id}'

    def subtotal(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.price_with_discount()
        super().save(*args, **kwargs)
        self.order.update_total_value()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.update_total_value()