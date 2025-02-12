from django.urls import path
from . import views

app_name = 'custom_admin'  # This adds the namespace

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('orders/', views.orders, name='orders'),
    path('customers/', views.customer_list, name='admin_customers'),
    path('catering/', views.catering, name='catering'),
    path('add_menu/', views.add_menu, name='add_menu'),
    path('add_category/', views.add_category, name='add_category'),
    path('menu_list/', views.menu_list, name='menu_list'),
    path('reservations/', views.reservations, name='reservations'),    
]
