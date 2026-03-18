from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, OrderAddress, Wishlist, Customer


# -----------------------
# CART
# -----------------------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    inlines = [CartItemInline]


# -----------------------
# ORDER ITEMS
# -----------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')
    can_delete = False


# -----------------------
# ORDER
# -----------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'total_amount',
        'payment_method',
        'payment_status',
        'order_status',
        'created_at'
    )

    list_filter = (
        'payment_status',
        'order_status',
        'payment_method'
    )

    search_fields = (
        'id',
        'user__username'
    )

    ordering = ('-created_at',)

    readonly_fields = (
        'user',
        'total_amount',
        'created_at'
    )

    date_hierarchy = 'created_at'

    inlines = [OrderItemInline]


# -----------------------
# ORDER ADDRESS
# -----------------------
@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'phone')


# -----------------------
# WISHLIST
# -----------------------
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')


# -----------------------
# CUSTOMER
# -----------------------
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')  # columns in admin
    search_fields = ('user__username', 'user__email', 'phone')