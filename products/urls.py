from django.urls import path
from . import views
from .views import add_to_cart

app_name = "products"   # 🔴 REQUIRED


urlpatterns = [
    
    path('', views.product_list, name='product_list'),
    path('search/', views.product_search, name='product_search'),
    path("add-to-cart/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path('<int:id>/', views.product_detail, name='product_detail'),

]