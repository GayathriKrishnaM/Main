from django.urls import path
from . import views

app_name = 'custom_admin'  # This adds the namespace

urlpatterns = [
    path('register/', views.admin_register, name='admin_register'),   
    path('login/', views.admin_login, name='admin_login'),
    path('profile/', views.admin_profile, name='admin_profile'),
    path('change-password/', views.admin_change_password, name='admin_change_password'),    
    path('logout/', views.admin_logout, name='admin_logout'),
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('orders/', views.view_orders, name='orders'),
    path('customers/', views.customer_list, name='admin_customers'),
    path('customers/edit/<int:pk>/', views.edit_customer, name='edit_customer'),
    path('customers/delete/<int:pk>/', views.delete_customer, name='delete_customer'),
    path('catering/', views.catering, name='catering'),
    path('add_menu/', views.add_menu, name='add_menu'),
    path('edit_menu/<int:pk>/', views.edit_menu, name='edit_menu'),
    path('delete_menu/<int:pk>/', views.delete_menu, name='delete_menu'),
    path('add_category/', views.add_category, name='add_category'),
    path('edit_category/<int:pk>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:pk>/', views.delete_category, name='delete_category'),
    path('category_list', views.category_list, name='category_list'),
    path('menu_list/', views.menu_list, name='menu_list'),
    path('reservations/', views.reservations, name='reservations'),
    path('events/', views.events, name='events'),
    path('staff_list/', views.staff_list, name='staff_list'),    
    path('staff_list/<int:pk>/edit/', views.staff_edit, name='edit_staff'),
    path('staff_list/<int:pk>/', views.staff_detail, name='staff_detail'),
    path('staff_delete/<int:pk>/', views.staff_delete, name='staff_delete'),
    path('add_staff/', views.add_staff, name='add_staff'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_inventory, name='add_inventory'),
    path('inventory/edit/<int:pk>/', views.edit_inventory, name='edit_inventory'),   
    # path('view_orders/', views.view_orders, name='view_orders'),
]
