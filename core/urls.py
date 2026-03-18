from django.contrib import admin
from django.urls import path, include
from core import views
from django.conf import settings
from django.conf.urls.static import static
from products import views as product_views

urlpatterns = [

 # Home & pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
  # Products
    path("products/", views.product_list, name="product_list"),  # ⭐ THIS LINE
    path('search/', views.product_search, name='product_search'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),

    # Categories
    path('categories/', views.categories, name='categories'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    # Cart & Orders
    path('cart/', views.cart_view, name='cart'),
    path('cart/increase/<int:product_id>/', views.cart_increase, name='cart_increase'),    
    path('cart/decrease/<int:product_id>/', views.cart_decrease, name='cart_decrease'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),     # Wishlist
    path('wishlist/', views.wishlist_page, name='wishlist_page'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),

    # Checkout & payment
    path('checkout/', views.checkout, name='checkout'),
    path('create-payment/', views.create_payment, name='create_payment'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),

 
    # Order success page
    path('order-success/', views.order_success, name='order_success'),
 
    path('my-account/', views.my_account, name='my_account'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)