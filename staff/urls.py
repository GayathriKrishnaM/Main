# staff/urls.py
from django.urls import path
from django.shortcuts import redirect
from .views import dashboard, staff_register, logout_and_redirect, profile, edit_profile
from django.contrib.auth import views as auth_views

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
]
