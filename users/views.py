from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserLoginForm

User = get_user_model()

def home(request):
    return render(request, 'users/home.html')


# ---------------- CUSTOMER LOGIN ----------------

def customer_login(request):
    next_url = request.GET.get("next") or request.POST.get("next")

    # prevent redirect loop
    if next_url in [request.path, "/users/login/", "/login/"]:
        next_url = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # check if user exists first
        from django.contrib.auth import get_user_model
        User = get_user_model()

        if not User.objects.filter(username=username).exists():
            messages.error(
                request,
                "You don't have an account. Please register first or Create Your Account."
            )
            return redirect(next_url or "/")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(next_url or "/products/")
        else:
            messages.error(
                request,
                "Incorrect password. Please try again or use 'Forgot Password'."
            )

    return render(request, "users/login.html", {"next": next_url})
# ---------------- CUSTOMER REGISTER ----------------
def customer_register(request):
    if request.user.is_authenticated:
        return redirect('/products/')   # ecommerce behavior

    next_url = request.POST.get("next") or request.GET.get("next")

    if not next_url or next_url in ["/login/", "/users/login/"]:
        next_url = None

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect(request.path)

        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists")
            return redirect(request.path)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect('/products/')

    return render(request, "users/register.html")

# ---------------- ADMIN LOGIN ----------------
def admin_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("/admin/")

        messages.error(request, "Invalid admin login")

    return render(request, "users/admin_login.html")  # 👈 Render a template



# ---------------- LOGOUT ----------------
def logout_user(request):
    logout(request)
    return redirect("home")



# ---------------- account ----------------


@login_required(login_url='users:login')
def my_account(request):
    user = request.user

    orders = Order.objects.filter(user=user)
    wishlist = Wishlist.objects.filter(user=user)

    return render(request, "core/my_account.html", {
        "orders": orders,
        "wishlist": wishlist,
    })