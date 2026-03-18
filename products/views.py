from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.urls import reverse
from core.models import Wishlist
from .models import Product
from django.contrib.auth.decorators import login_required
from core.models import Order, OrderItem

def products(request):
    products = Product.objects.filter(is_active=True)

    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    return render(request, 'products.html', {
        'products': products,
        'wishlist_products': wishlist_products,
    })



def product_search(request):
    query = request.GET.get('q', '').strip()

    products = Product.objects.filter(
        is_active=True
    ).filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )

    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    return render(request, 'core/search_results.html', {
        'products': products,
        'query': query,
        'wishlist_products': wishlist_products,
        'star_range': range(1, 6),  # ⭐ ADD THIS

    })


def product_list(request):
    products = Product.objects.all()
    return render(request, 'core/product_list.html', {
        'products': products
    })



def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    # Temporary safe defaults (prevents template crash)
    wishlist_products = []

    return render(request, 'core/product_detail.html', {
        'product': product,
        'wishlist_products': wishlist_products,
    })
    

@login_required(login_url='users:login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    order, created = Order.objects.get_or_create(
        user=request.user,
        order_status="Pending"
    )

    item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product
    )

    if not created:
        item.quantity += 1
        item.save()

    # 🔁 return to SAME page
    return redirect(request.GET.get("next", "/products/"))


