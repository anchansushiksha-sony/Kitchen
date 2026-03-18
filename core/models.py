from django.db import models
from django.conf import settings
from products.models import Product
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


User = get_user_model()

 # --------------------
# CART
# --------------------
class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    @property
    def total_price(self):
        """Compute the total price of all items in the cart."""
        total = sum(item.product.price * item.quantity for item in self.items.all())
        return total

    def __str__(self):
        return f"Cart - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# --------------------
# ORDER
# --------------------
class Order(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash On Delivery'),
        ('ONLINE', 'Online Payment'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='COD')
    payment_status = models.BooleanField(default=False)
    order_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


# --------------------
# ORDER ITEMS
# --------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # 👈 IMPORTANT
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# --------------------
# ORDER ADDRESS
# --------------------
class OrderAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name



class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
            return f"{self.user.username} - {self.product.name}"



class Customer(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer"
    )

    phone = models.CharField(max_length=15, blank=True, null=True)

    address = models.TextField(blank=True, null=True)

    city = models.CharField(max_length=100, blank=True, null=True)

    state = models.CharField(max_length=100, blank=True, null=True)

    pincode = models.CharField(max_length=10, blank=True, null=True)

    country = models.CharField(max_length=100, default="India")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Customer"

# ----------------------------
# Automatically Create Customer
# ----------------------------
@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_customer(sender, instance, **kwargs):
    if hasattr(instance, "customer"):
        instance.customer.save()