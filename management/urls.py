from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_customer, name='register'),
    path('login/', views.login_customer, name='login'),
    path('logout/', views.logout_customer, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('menu/', views.menu_view, name='menu'),
    path('menu/<int:menu_id>/', views.menu_detail, name='menu_detail'),
    path('add_to_cart/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('table_reservation/', views.table_reservation, name='table_reservation'),
    path('reservation_history/', views.reservation_history, name='reservation_history'),
    path('plan_event/', views.plan_event, name='plan_event'),
    path('event_history/', views.event_history, name='event_history'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('notifications/', views.notifications, name='notifications'),
]
