from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import (
    Customer, Menu, Category, MenuVariant, Order, OrderItem, TableReservation,
    EventPlan, Feedback, Notification
)

def home(request):
    return render(request, 'home.html')

# User Registration View
def register_customer(request):
    if request.method == 'POST':
        # Extract form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        mobile = request.POST.get('mobile')
        dob = request.POST.get('dob')  # Extract dob
        place = request.POST.get('place')  # Extract place
        city = request.POST.get('city')  # Extract city
        pin = request.POST.get('pin')  # Extract pin

        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        # Create User
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create Customer Profile
        customer = Customer.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            mobile=mobile,
            dob=dob if dob else None,
            place=place,
            city=city,
            pin=pin,
        )

        # Log the user in
        login(request, user)
        messages.success(request, 'Registration successful.')
        return redirect('home')

    return render(request, 'management/register.html')

# User Login View
def login_customer(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return redirect('login')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'management/login.html')

# User Logout View
@login_required
def logout_customer(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# Profile View
@login_required
def profile(request):
    customer = request.user.customer_profile

    if request.method == 'POST':
        # Update profile information
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        dob = request.POST.get('dob')
        place = request.POST.get('place')
        city = request.POST.get('city')
        pin = request.POST.get('pin')

        customer.full_name = full_name
        customer.mobile = mobile
        customer.dob = dob if dob else None
        customer.place = place
        customer.city = city
        customer.pin = pin
        customer.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return render(request, 'management/profile.html', {'customer': customer})

# Menu Display View
def menu_view(request):
    menus = Menu.objects.all()
    return render(request, 'management/menu.html', {'menus': menus})

# Menu Details View
def menu_detail(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)
    variants = menu.variants.all()
    return render(request, 'management/menu_detail.html', {'menu': menu, 'variants': variants})

def category_list(request):
    # Optional: a view to list all categories
    categories = Category.objects.all()
    return render(request, 'management/category_list.html', {'categories': categories})

# Add to Cart View
@login_required
def add_to_cart(request, variant_id):
    variant = get_object_or_404(MenuVariant, id=variant_id)
    quantity = int(request.POST.get('quantity', 1))

    # Get or create an active order for the customer
    order, created = Order.objects.get_or_create(
        customer=request.user.customer_profile,
        order_status='pending',
        defaults={'date_time': timezone.now()}
    )

    # Add item to the order
    order_item = OrderItem.objects.create(
        order=order,
        menu_variant=variant,
        quantity=quantity,
        price=variant.price,
        discount=variant.menu.discount,
    )

    # Update order totals
    order.total_amount += variant.price * quantity
    order.total_discount += variant.menu.discount * quantity
    order.save()

    messages.success(request, 'Item added to cart.')
    return redirect('cart')

# Cart View
@login_required
def cart_view(request):
    try:
        order = Order.objects.get(customer=request.user.customer_profile, order_status='pending')
        order_items = order.items.all()
    except Order.DoesNotExist:
        order = None
        order_items = None

    return render(request, 'management/cart.html', {'order': order, 'order_items': order_items})

# Remove Item from Cart
@login_required
def remove_from_cart(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id, order__customer=request.user.customer_profile)
    order = order_item.order

    # Update order totals
    order.total_amount -= order_item.price * order_item.quantity
    order.total_discount -= order_item.discount * order_item.quantity
    order.save()

    order_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')

# Checkout View
@login_required
def checkout(request):
    try:
        order = Order.objects.get(customer=request.user.customer_profile, order_status='pending')
    except Order.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('menu')

    if request.method == 'POST':
        # Process payment logic here (skipped for brevity)
        order.order_status = 'confirmed'
        order.payment_status = 'completed'
        order.date_time = timezone.now()
        order.save()
        messages.success(request, 'Order placed successfully.')
        return redirect('order_history')

    return render(request, 'management/checkout.html', {'order': order})

# Order History View
@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user.customer_profile).exclude(order_status='pending')
    return render(request, 'management/order_history.html', {'orders': orders})

# Order Details View
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer_profile)
    return render(request, 'management/order_detail.html', {'order': order})

# Table Reservation View
@login_required
def table_reservation(request):
    if request.method == 'POST':
        table_id = request.POST.get('table_id')
        guest_count = int(request.POST.get('guest_count'))
        date = request.POST.get('date')
        time = request.POST.get('time')
        booking_fee = float(request.POST.get('booking_fee', 0))

        # Create reservation
        reservation = TableReservation.objects.create(
            customer=request.user.customer_profile,
            table_id=table_id,
            guest_count=guest_count,
            date=date,
            time=time,
            booking_fee=booking_fee,
            booking_status='pending',
            payment_status='pending',
        )

        messages.success(request, 'Table reservation requested. We will confirm shortly.')
        return redirect('reservation_history')

    return render(request, 'management/table_reservation.html')

# Reservation History View
@login_required
def reservation_history(request):
    reservations = TableReservation.objects.filter(customer=request.user.customer_profile)
    return render(request, 'management/reservation_history.html', {'reservations': reservations})

# Event Planning View
@login_required
def plan_event(request):
    if request.method == 'POST':
        event_date = request.POST.get('event_date')
        guest_count = int(request.POST.get('guest_count'))
        custom_dish = request.POST.get('custom_dish', '')
        amount = float(request.POST.get('amount', 0))
        advance_amount = float(request.POST.get('advance_amount', 0))

        # Create event plan
        event_plan = EventPlan.objects.create(
            customer=request.user.customer_profile,
            guest_count=guest_count,
            custom_dish=custom_dish,
            event_date=event_date,
            amount=amount,
            advance_amount=advance_amount,
            payment_status='pending',
        )

        # Add selected menu items
        menu_item_ids = request.POST.getlist('menu_items')
        menu_items = MenuVariant.objects.filter(id__in=menu_item_ids)
        event_plan.menu_items.set(menu_items)
        event_plan.save()

        messages.success(request, 'Event plan submitted. We will contact you for confirmation.')
        return redirect('event_history')

    menu_variants = MenuVariant.objects.all()
    return render(request, 'management/plan_event.html', {'menu_variants': menu_variants})

# Event History View
@login_required
def event_history(request):
    events = EventPlan.objects.filter(customer=request.user.customer_profile)
    return render(request, 'management/event_history.html', {'events': events})

# Submit Feedback View
@login_required
def submit_feedback(request):
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comments = request.POST.get('comments', '')

        Feedback.objects.create(
            customer=request.user.customer_profile,
            rating=rating,
            comments=comments,
            date=timezone.now(),
        )

        messages.success(request, 'Thank you for your feedback!')
        return redirect('home')

    return render(request, 'management/submit_feedback.html')

# Notification View
@login_required
def notifications(request):
    notifications = Notification.objects.filter(customer=request.user.customer_profile)
    return render(request, 'management/notifications.html', {'notifications': notifications})

# View for Home Page
def home(request):
    return render(request, 'management/home.html')
