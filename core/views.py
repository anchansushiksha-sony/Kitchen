
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Avg
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction

import razorpay

from .forms import RatingForm
from products.models import Product, Category, Rating
from core.models import Wishlist, Order, OrderItem, OrderAddress, Customer
from django.contrib.auth import get_user_model

User = get_user_model()

# Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

# -------------------- HOME --------------------
def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:4]
    new_products = Product.objects.filter(is_active=True).order_by('-created_at')[:4]

    return render(request, 'core/index.html', {
        'categories': categories,
        'featured_products': featured_products,
        'new_products': new_products,
    })


# -------------------- STATIC PAGES --------------------
def about(request):
    return render(request, "core/about.html")


def contact(request):
    if request.method == "POST":
        messages.success(request, "Thank you! Your message has been sent.")
        return redirect("contact")

    return render(request, "core/contact.html")
# -------------------- Categories --------------------
def categories(request):
    return render(request, 'core/categories.html')


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    products = Product.objects.filter(category=category, is_active=True)

    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)

    return render(request, "core/category_products.html", {
        "category": category,
        "products": products,
        "wishlist_products": wishlist_products
    })

# -------------------- PRODUCTS --------------------
def product_list(request):
    products = Product.objects.filter(is_active=True)

    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    return render(request, "core/product_list.html", {
        "products": products,
        "wishlist_products": wishlist_products
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    ratings = product.ratings.all()
    avg_rating = ratings.aggregate(average=Avg('value'))['average'] or 0
    avg_rating = round(avg_rating, 1)

    user_rating = None
    form = None

    if request.user.is_authenticated:
        user_rating = ratings.filter(user=request.user).first()

        if request.method == "POST":
            form = RatingForm(request.POST, instance=user_rating)
            if form.is_valid():
                rating = form.save(commit=False)
                rating.product = product
                rating.user = request.user
                rating.save()
                return redirect('product_detail', product_id=product.id)

        if not form:
            form = RatingForm(instance=user_rating)

    return render(request, 'core/product_detail.html', {
        'product': product,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'form': form,
        'user_rating': user_rating,
        'star_range': range(1, 6),
    })


def product_search(request):
    query = request.GET.get('q', '').strip()

    results = Product.objects.filter(is_active=True)

    if query:
        results = results.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

    return render(request, 'core/search_results.html', {
        'query': query,
        'results': results
    })


# -------------------- CART --------------------
@login_required(login_url='users:login')
def cart_view(request):

    order = Order.objects.filter(
        user=request.user,
        order_status="Pending"
    ).first()

    products = []
    total_price = 0

    if order:
        products = OrderItem.objects.filter(order=order)

        for item in products:
            item.subtotal = item.price * item.quantity
            total_price += item.subtotal

    return render(request, "core/cart.html", {
        "products": products,
        "total_price": total_price
    })


@login_required(login_url='users:login')
def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    order, created = Order.objects.get_or_create(
        user=request.user,
        order_status="Pending"
    )

    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={
            "price": product.price,
            "quantity": 1
        }
    )

    if not created:
        order_item.quantity += 1
        order_item.save()

    return redirect('cart')


@login_required(login_url='users:login')
def cart_increase(request, product_id):
    item = OrderItem.objects.get(order__user=request.user, product_id=product_id)
    item.quantity += 1
    item.save()
    return redirect('cart')


@login_required(login_url='users:login')
def cart_decrease(request, product_id):

    order = Order.objects.filter(
        user=request.user,
        order_status="Pending"
    ).first()

    if not order:
        return redirect("cart")

    order_item = OrderItem.objects.filter(
        order=order,
        product_id=product_id
    ).first()   # ⭐ changed from get() to first()

    if order_item:
        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
        else:
            order_item.delete()

    return redirect("cart")






@login_required(login_url='users:login')
def cart_remove(request, product_id):

    item = get_object_or_404(
        OrderItem,
        product_id=product_id,
        order__user=request.user,
        order__order_status="Pending"
    )

    item.delete()

    return redirect("cart")

def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # you can add order/cart logic later
    return redirect('cart')
# -------------------- WISHLIST --------------------
@login_required(login_url='users:login')
def wishlist_page(request):

    wishlist = Wishlist.objects.filter(user=request.user)

    return render(request, "core/wishlist.html", {
        "wishlist": wishlist
    })


@login_required(login_url='users:login')
def wishlist_toggle(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
    else:
        Wishlist.objects.create(
            user=request.user,
            product=product
        )

    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


# -------------------- CHECKOUT --------------------
@login_required(login_url='users:login')
def checkout(request):

    order = Order.objects.filter(
    user=request.user,
    order_status="Pending"
    ).first()

    if not order:
        return redirect("cart")

    items = OrderItem.objects.filter(order=order)
    total = sum(item.product.price * item.quantity for item in items)

    return render(request, "core/checkout.html", {
    "order": order,
    "items": items,
    "total": total,
    "razorpay_key": settings.RAZORPAY_KEY_ID   # 👈 ADD THIS LINE
})


# -------------------- PAYMENT --------------------
@login_required(login_url='users:login')
def create_payment(request):

    order = Order.objects.filter(
        user=request.user,
        order_status="Pending"
    ).first()

    if not order:
        return JsonResponse({"error": "No order found"}, status=400)

    items = OrderItem.objects.filter(order=order)

    total = sum(item.product.price * item.quantity for item in items)

    if total == 0:
        return JsonResponse({"error": "Cart is empty"}, status=400)

    payment = razorpay_client.order.create({
        "amount": int(total * 100),   # ₹ → paise
        "currency": "INR",
        "payment_capture": "1"
    })

    return JsonResponse({
        "id": payment["id"],
        "amount": payment["amount"]
    })
@login_required(login_url='users:login')
def verify_payment(request):
    return redirect("order_success")


# -------------------- SUCCESS --------------------
def order_success(request):
    return render(request, "core/order_success.html")


# -------------------- AUTH --------------------
def customer_login(request):
    next_url = request.GET.get('next') or request.POST.get('next')

    # 🚫 prevent redirect loop
    if next_url in ["/login/", "/users/login/"]:
        next_url = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if next_url:
                return redirect(next_url)

            return redirect("product_list")

        else:
            messages.error(request, "Invalid username or password")

    return render(request, "users/login.html", {"next": next_url})


def customer_register(request):

    next_url = request.POST.get("next") or request.GET.get("next")

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # check passwords
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("users:register") 

        # create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        if next_url:
            return redirect(next_url)

        return redirect("product_list")

    return render(request, "users/register.html", {"next": next_url})

    




@login_required(login_url='users:login')
def my_account(request):
    user = request.user

    orders = Order.objects.filter(user=user)
    wishlist = Wishlist.objects.filter(user=user)

    return render(request, "core/my_account.html", {
        "orders": orders,
        "wishlist": wishlist,
    })
