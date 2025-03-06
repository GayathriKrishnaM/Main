from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_customer, name='register'),
    path('login/', views.login_customer, name='login'),
    path('logout/', views.logout_customer, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('menu/', views.menu_view, name='menu'),
    path('menu/category/<int:category_id>/', views.menu_view, name='menu_category'),
    path('menu/<int:menu_id>/', views.menu_detail, name='menu_detail'),
    path('add_to_cart/<int:menu_id>/', views.add_to_cart, name='add_to_cart'),
    path('order-now/<int:menu_id>/', views.order_now, name='order_now'),
    path('cart/', views.cart_view, name='cart'),
    path('update-cart/<int:menu_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),  # New URL pattern
    path('order_history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('table_reservation/', views.table_reservation, name='table_reservation'),
    path('confirm_reservation_payment/', views.confirm_reservation_payment, name='confirm_reservation_payment'),  # Add this line    
    path('reservation_history/', views.reservation_history, name='reservation_history'),
    path('reservation/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),  # Add this line
    path('plan_event/', views.plan_event, name='plan_event'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),  # Add this line
    path('event_history/', views.event_history, name='event_history'),
    path('confirm_event_payment/', views.confirm_event_payment, name='confirm_event_payment'),  # Add this line
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('notifications/', views.notifications, name='notifications'),
]
