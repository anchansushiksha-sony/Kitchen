from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.customer_register, name='register'),
    path('login/', views.customer_login, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_user, name='logout'),
]
