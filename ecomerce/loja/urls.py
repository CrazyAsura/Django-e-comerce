# loja/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Rota para a função 'home' na view
    path('product/', views.product, name='product'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product_detail/<int:product_id>/add-to-cart', views.add_to_cart, name='add_to_cart'),
    path('categories/', views.categories, name='categories'),
    path('categories/products-by-category/<int:category_id>/', views.products_by_category, name='products_by_category'),
    path('offers/', views.offers, name='offers'),
    path('cart-with-login/', views.cart_view_with_login, name='cart_view_with_login'),
    path('cart-without-login/', views.cart_view_without_login, name='cart_view_without_login'),
    path('cart/update/<int:item_id>/', views.cart_update_quantity, name='cart_update_quantity'),
    path('cart/remove/<int:item_id>/', views.cart_remove_item, name='cart_remove_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('register/', views.register, name='register'),
    path('login', views.login, name='login'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('faq/', views.faq, name='faq'),
    path('privacy-policy', views.privacy_policy, name='privacy_policy'),
    path('terms-of-use', views.terms_of_use, name='terms_of_use'),
    path('api/search/', views.search_products, name='search_products'),
]
