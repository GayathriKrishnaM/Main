# staff/urls.py
from django.urls import path
from django.shortcuts import redirect
from .views import dashboard, staff_register, logout_and_redirect, profile, edit_profile
from django.contrib.auth import views as auth_views
from . import views

def index(request):
    return redirect('staff_dashboard')

urlpatterns = [
    path('', index, name='staff_index'),  # This handles /staff/ and redirects
    path('dashboard/', dashboard, name='staff_dashboard'),
    path('profile/', profile, name='staff_profile'),    
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('register/', staff_register, name='staff_register'),
    path('login/', auth_views.LoginView.as_view(template_name='staff/staff_login.html'), name='staff_login'),
    path('logout/', logout_and_redirect, name='staff_logout'),
    path('view_orders/<int:order_id>/', views.view_orders, name='view_orders'),
    path('view_reservations/<int:reservation_id>/', views.view_reservations, name='view_reservations'),
    path('view_event_plan/<int:event_id>/', views.view_event_plan, name='view_event_plan'),
    path('view_customers/', views.view_customers, name='view_customers'),
    path('all_orders/', views.all_orders, name='all_orders'),
    path('all_reservations/', views.all_reservations, name='all_reservations'),
    path('all_events/', views.all_events, name='all_events'),
    path('update-delivery-status/<int:order_id>/', views.update_delivery_status, name='update_delivery_status'),

]
