"""
The `views.py` module in the `loja` app defines the Django views for the e-commerce website.

The views include:
- `home`: Renders the home page with a list of all products.
- `product`: Renders the product page with a list of all products.
- `product_detail`: Renders the detail page for a specific product.
- `categories`: Renders the categories page with a list of all categories.
- `products_by_category`: Renders the page with products for a specific category.
- `offers`: Renders the offers page with a list of products with discounts.
- `register`: Handles the user registration process, including creating a user, address, and phone number.
- `login`: Handles the user login process, authenticating the user and redirecting to the home page.
- `password_reset`: Handles the password reset process, allowing users to change their password.
- `shopping_cart`: Renders the shopping cart page.
- `checkout`: Handles the checkout process, creating a new order and transferring items from the cart to the order.
- `order_detail`: Renders the order detail page for a specific order.
- `faq`: Renders the FAQ page.
- `privacy_policy`: Renders the privacy policy page.
- `terms_of_use`: Renders the terms of use page.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Category, User, Cart, CartItem, Order, OrderItem, Address
from .forms import UserForm, AddressForm, PhoneForm, LoginForm 
import stripe
from django.conf import settings
from django.db import transaction


def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'home.html', {'products': products, 'categories': categories})

def product(request):
    products = Product.objects.all()
    return render(request, 'product.html', {'products': products})

def product_detail(request, product_id):
    products = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'products': products})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Verifica se o produto tem estoque disponível
    if product.stock < 1:
        messages.error(request, 'Este produto está fora de estoque.')
        return redirect('product_detail', product_id=product_id)

    # Obtém ou cria o carrinho do usuário
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Verifica se o produto já está no carrinho
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        # Incrementa a quantidade do item no carrinho
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'{product.name} adicionado ao carrinho.')
        else:
            messages.error(request, 'Não há estoque suficiente para adicionar mais unidades deste produto.')
    else:
        cart_item.quantity = 1
        cart_item.save()
        messages.success(request, f'{product.name} adicionado ao carrinho.')

    return redirect('cart_view')

def categories(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})

def products_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'products_by_category.html', {'category': category, 'products': products})

def offers(request):
    products = Product.objects.filter(discount__gt=0).order_by('-discount')
    categories = Category.objects.all()  # Filtrar categorias, se necessário.
    return render(request, 'offers.html', {
        'products': products,
        'total_offers': products.count(),
        'categories': categories,
    })

from django.db.models import Q

def search_products(request):
    query = request.GET.get('q', '').strip()
    if query:
        # Use Q objects for better readability and potential further optimization
        produtos = Product.objects.filter(
            Q(nome__icontains=query) | Q(descricao__icontains=query)
        ).only('id', 'nome', 'imagem', 'preco')[:10]  # Optimize by selecting only necessary fields
        
        results = [{
            'url': f"/produto/{produto.id}/",
            'name': produto.nome,
            'image': produto.imagem.url if produto.imagem else '/static/default-product.jpg',
            'price': produto.preco
        } for produto in produtos]
        
        return JsonResponse(results, safe=False)

    return JsonResponse([], safe=False)

def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        address_form = AddressForm(request.POST)
        phone_form = PhoneForm(request.POST)
        
        if user_form.is_valid() and address_form.is_valid() and phone_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save(commit=False)
                    user.set_password(user_form.cleaned_data['password'])  # Salvar senha como hash
                    user.save()

                    address = address_form.save(commit=False)
                    address.user = user
                    address.save()

                    phone = phone_form.save(commit=False)
                    phone.user = user
                    phone.save()

                    messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
                    return redirect('login')
            except Exception as e:
                messages.error(request, f'Ocorreu um erro ao salvar os dados: {e}')
        else:
            # Exibir erros específicos de cada formulário
            user_errors = user_form.errors.as_json()
            address_errors = address_form.errors.as_json()
            phone_errors = phone_form.errors.as_json()

            messages.error(request, f"Erro no formulário de usuário: {user_errors}")
            messages.error(request, f"Erro no formulário de endereço: {address_errors}")
            messages.error(request, f"Erro no formulário de telefone: {phone_errors}")
    else:
        user_form = UserForm()
        address_form = AddressForm()
        phone_form = PhoneForm()

    return render(request, "register.html", {
        'user_form': user_form,
        'address_form': address_form,
        'phone_form': phone_form
    })


def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Bem-vindo, {user.username}!')
                return redirect('home')  # Substitua 'home' pela URL da sua página inicial
            else:
                messages.error(request, 'Usuário ou senha inválidos. Tente novamente.')
        else:
            messages.error(request, 'Preencha os campos corretamente.')

    else:
        login_form = LoginForm()

    return render(request, 'login.html', {'login_form': login_form})

def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        try:
            user = User.objects.get(email=email)
            if new_password == confirm_password:
                if len(new_password) >= 8:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Password changed successfully.')
                    return redirect('login')
                else:
                    messages.error(request, 'Password must be at least 8 characters long.')
            else:
                messages.error(request, 'Passwords do not match.')
        except User.DoesNotExist:
            messages.error(request, 'Email not found.')
            
    return render(request, 'password_reset.html')

def cart_view_without_login(request):
    return render(request, 'cart_without_login.html')
    

@login_required
def cart_view_with_login(request):
    # Obtém ou cria o carrinho do usuário
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Calcula o total do carrinho
    cart_total = cart.total_price()

    # Renderiza a página do carrinho
    return render(request, 'cart_with_login.html', {
        'cart': cart,
        'cart_total': cart_total,
    })

@login_required
@require_POST
def cart_update_quantity(request, item_id):
    # Obtém o item do carrinho com o id fornecido
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    # Obtém a nova quantidade enviada via POST
    new_quantity = request.POST.get('quantity')

    # Verifica se a nova quantidade é válida
    if new_quantity.isdigit():
        new_quantity = int(new_quantity)
        
        if new_quantity > 0:
            # Atualiza a quantidade do item no carrinho
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, 'Quantidade atualizada com sucesso.')
        else:
            messages.error(request, 'A quantidade deve ser maior que zero.')
    else:
        messages.error(request, 'Quantidade inválida.')

    # Redireciona de volta para a página do carrinho
    return redirect('cart_view')


@login_required
@require_POST
def cart_remove_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart_view')

# Configuração do Stripe com a chave secreta
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@login_required
def checkout(request):
    # Obtém o carrinho do usuário
    cart = Cart.objects.filter(user=request.user).first()

    if not cart or cart.items.count() == 0:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('cart_view')

    # Cálculo do valor total do pedido
    total_amount = int(cart.total_price() * 100)  # O Stripe usa centavos, então multiplicamos por 100

    if request.method == "POST":
        # Recebe o token do cliente (gerado pelo Stripe.js)
        token = request.POST.get('stripeToken')

        if not token:
            messages.error(request, 'Erro ao processar o pagamento. Tente novamente.')
            return redirect('checkout')

        try:
            # Cria uma cobrança (charge) no Stripe
            charge = stripe.Charge.create(
                amount=total_amount,
                currency="brl",  # Pode ser outra moeda, se necessário
                description="Compra no e-commerce",
                source=token,
            )

            # Verificar se a cobrança foi bem-sucedida
            if charge['status'] == 'succeeded':
                # Criar o pedido no banco de dados
                order = Order.objects.create(
                    user=request.user,
                    total_value=cart.total_price(),
                    status='paid',  # Pode ter status como "paid" ou "pending"
                )

                # Transferir os itens do carrinho para o pedido
                for item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.product.price
                    )

                # Limpar o carrinho após pagamento
                cart.items.all().delete()

                messages.success(request, 'Pagamento realizado com sucesso!')
                return redirect('order_detail', order_id=order.id)

            else:
                messages.error(request, 'Falha ao processar o pagamento. Tente novamente.')
                return redirect('checkout')

        except stripe.error.CardError as e:
            messages.error(request, f'Erro no pagamento: {e.user_message}')
        except stripe.error.StripeError as e:
            messages.error(request, 'Erro de sistema com o Stripe. Tente novamente mais tarde.')
        except Exception as e:
            messages.error(request, f'Erro inesperado: {str(e)}')

    else:
        # Passa a chave pública do Stripe para o template
        context = {
            'cart': cart,
            'stripe_public_key': settings.STRIPE_TEST_PUBLIC_KEY,
            'total_amount': cart.total_price(),
        }
        return render(request, 'checkout.html', context)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET  # Configure esse segredo no seu ambiente

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        # Trata o evento 'payment_intent.succeeded'
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            order_id = payment_intent['metadata']['order_id']  # Armazene o order_id no metadata
            order = Order.objects.get(id=order_id)

            # Atualiza o status do pedido
            order.status = 'paid'
            order.save()

        return JsonResponse({'status': 'success'})
    except ValueError as e:
        # Assumimos que o payload é inválido
        return JsonResponse({'status': 'failure'}, status=400)


def order_detail(request, order_id):
    orders = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_detail.html', {'orders': orders})   

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')

def faq(request):
    return render(request, 'faq.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_use(request):
    return render(request, 'terms_of_use.html')