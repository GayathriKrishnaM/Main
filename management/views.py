from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import (
    Customer, Menu, Category, MenuVariant, Order, OrderItem, TableReservation,
    EventPlan,Catering, Feedback, Notification, Payment, Preorder, Inventory
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
        user = authenticate(username=username, password=password)
        # Log the user in
        login(request, user, backend='management.backends.EmailOrUsernameBackend')  # Specify the correct backend        messages.success(request, 'Registration successful.')
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
@login_required(login_url='/login/')  # Change to your desired login URL
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

from django.shortcuts import render, get_object_or_404

def menu_view(request, category_id=None):
    categories = Category.objects.all()
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        menu_items = Menu.objects.filter(category=category)
        active_category_id = category.id
    else:
        menu_items = Menu.objects.all()
        active_category_id = None
    context = {
        'categories': categories,
        'menu_items': menu_items,
        'active_category_id': active_category_id,
    }
    return render(request, 'management/menu.html', context)

def menu_detail(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)
    variants = menu.variants.all()
    return render(request, 'management/menu_detail.html', {'menu': menu, 'variants': variants})

def category_list(request):
    # Optional: a view to list all categories
    categories = Category.objects.all()
    return render(request, 'management/category_list.html', {'categories': categories})

# Add to Cart View
@login_required(login_url='/login/')  # Change to your desired login URL
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
@login_required(login_url='/login/')  # Change to your desired login URL
def cart_view(request):
    try:
        order = Order.objects.get(customer=request.user.customer_profile, order_status='pending')
        order_items = order.items.all()
        # Calculate subtotal for each item
        for item in order_items:
            item.subtotal = item.price * item.quantity
        total = sum(item.subtotal for item in order_items)
    except Order.DoesNotExist:
        order = None
        order_items = []
        total = 0

    return render(request, 'management/cart.html', {'order': order, 'order_items': order_items, 'total': total})

# Remove Item from Cart
@login_required(login_url='/login/')  # Change to your desired login URL
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

import razorpay
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect

@login_required(login_url='/login/')  # Change to your desired login URL
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('menu')

    total = sum(item['price'] * item['quantity'] for item in cart.values())
    total_paise = int(total * 100)  # Convert to paise

    # Razorpay client initialization with SSL verification disabled
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET), verify=False)

    # Create a Razorpay Order
    razorpay_order = client.order.create({
        "amount": total_paise,
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        'cart': cart,
        'total': total,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'currency': 'INR'
    }
    return render(request, 'management/checkout.html', context)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required(login_url='/login/')  # Change to your desired login URL
def place_order(request):
    if request.method == 'POST':
        # Get the cart from the session
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Your cart is empty.")
            return redirect('menu')

        # Razorpay payment details
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Verify payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed.")
            return redirect('checkout')

        customer = request.user.customer_profile
        # Create a new Order instance
        order = Order.objects.create(
            customer=customer,
            date_time=timezone.now(),
            order_status='pending',
            payment_status='completed',
            delivery_status='pending',
            total_amount=0,
            total_discount=0,
        )

        total_amount = 0
        total_discount = 0
        # Iterate over cart items to create OrderItem instances
        for key, item in cart.items():
            menu_id = int(key)  # Convert key back to integer
            menu = get_object_or_404(Menu, id=menu_id)
            quantity = item['quantity']
            price = Decimal(item['price'])  # Ensure it's a Decimal
            discount = Decimal(item.get('discount', 0))  # Get discount if available
            total_price = price * quantity
            total_disc = discount * quantity

            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                menu=menu,  # Adjust if using MenuVariant
                quantity=quantity,
                price=price,
                discount=discount,
            )
            total_amount += total_price
            total_discount += total_disc

        # Update order totals
        order.total_amount = total_amount
        order.total_discount = total_discount
        order.save()

        # Create Payment instance
        Payment.objects.create(
            customer=customer,
            service_type='order',  # Assuming this is an order payment
            date=timezone.now(),
            amount=total_amount,
            method='online',  # Assuming the payment method is online
            status='completed',
        )

        # Clear the cart
        request.session['cart'] = {}
        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_history')  # Redirect to 'My Orders'
    else:
        return redirect('checkout')

# Order History View
@login_required(login_url='/login/')  # Change to your desired login URL
def order_history(request):
    orders = Order.objects.filter(customer=request.user.customer_profile).order_by('-date_time')     
    # .exclude(order_status='pending')
    return render(request, 'management/order_history.html', {'orders': orders})

# Order Details View
@login_required(login_url='/login/')  # Change to your desired login URL
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer_profile)
    return render(request, 'management/order_detail.html', {'order': order})

from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
import razorpay
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')  # Change to your desired login URL
def table_reservation(request):
    if request.method == 'POST':
        guest_count = int(request.POST.get('guest_count'))
        date = request.POST.get('date')
        time = request.POST.get('time')
        menu_items = request.POST.getlist('menu_items')
        
        # Set default table ID
        table_id = 1

        # Calculate booking fee based on guest count
        if guest_count == 1:
            booking_fee = 100
        elif guest_count == 2:
            booking_fee = 150
        elif guest_count == 3 or guest_count == 4:
            booking_fee = 200
        elif 4 < guest_count <= 6:
            booking_fee = 300
        elif guest_count <= 10:
            booking_fee = 350
        else:
            messages.error(request, "Guest count exceeds the allowed limit.")
            return redirect('table_reservation')

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

        # Handle preorders
        preorders = []
        if menu_items:
            for item_id in menu_items:
                menu_item = Menu.objects.get(id=item_id)
                preorder = Preorder.objects.create(
                    reservation=reservation,
                    menu=menu_item,
                    quantity=1,  # Assuming a default quantity
                    price=menu_item.price,
                )
                preorders.append(preorder)

        # Store reservation_id in the session
        request.session['reservation_id'] = reservation.id

        total_paise = int(booking_fee * 100)  # Convert to paise

        # Razorpay client initialization with SSL verification disabled
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET), verify=False)

        # Create a Razorpay Order
        razorpay_order = client.order.create({
            "amount": total_paise,
            "currency": "INR",
            "payment_capture": "1"
        })

        context = {
            'reservation': reservation,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'currency': 'INR',
            'booking_fee': booking_fee,
            'preorders': preorders,
        }
        return render(request, 'management/confirm_payment.html', context)
    else:
        # Handle category selection and display menu items (if needed)
        category_id = request.GET.get('category_id')
        if category_id:
            menus = Menu.objects.filter(category_id=category_id)
        else:
            menus = None

        # Create time slots in 1-hour intervals from 7:00 AM to 7:00 PM
        time_slots = [f"{hour:02}:00" for hour in range(7, 20)]  # 07:00 to 19:00
        categories = Category.objects.all()
        context = {
            'time_slots': time_slots,
            'categories': categories,
            'menus': menus,
        }
        return render(request, 'management/table_reservation.html', context)

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
import razorpay

@csrf_exempt
@login_required(login_url='/login/')  # Change to your desired login URL
def confirm_reservation_payment(request):
    if request.method == 'POST':
        # Razorpay payment details
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Verify payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET), verify=False)
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed.")
            return redirect('reservation_history')

        # Retrieve the reservation
        reservation_id = request.session.get('reservation_id')
        reservation = get_object_or_404(TableReservation, id=reservation_id)

        # Update reservation status
        reservation.payment_status = 'completed'
        reservation.booking_status = 'confirmed'
        reservation.save()

        # Create Payment instance
        Payment.objects.create(
            customer=request.user.customer_profile,
            service_type='reservation',  # Reservation payment
            date=timezone.now(),
            amount=reservation.booking_fee,
            method='online',
            status='completed',
        )

        messages.success(request, "Your reservation has been confirmed and payment completed!")
        return redirect('reservation_history')
    else:
        return redirect('reservation_history')
    
def reservation_history(request):
    reservations = TableReservation.objects.filter(customer=request.user.customer_profile).order_by('-date')
    return render(request, 'management/reservation_history.html', {'reservations': reservations})   

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from .models import EventPlan, Menu, Catering

# @login_required(login_url='/login/')  # Change to your desired login URL
# def plan_event(request):
#     if request.method == 'POST':
#         event_date = request.POST.get('event_date')
#         guest_count = int(request.POST.get('guest_count'))
#         custom_dish = request.POST.get('custom_dish', '')
#         amount = float(request.POST.get('amount', 0))
#         advance_amount = float(request.POST.get('advance_amount', 0))
#         catering_service = request.POST.get('catering_service')
#         event_type = request.POST.get('event_type')
#         other_event_type = request.POST.get('other_event_type', '')

#         # Create the event plan
#         event_plan = EventPlan.objects.create(
#             customer=request.user.customer_profile,
#             guest_count=guest_count,
#             custom_dish=custom_dish,
#             event_date=event_date,
#             amount=amount,
#             advance_amount=advance_amount,
#             payment_status='pending',
#             event_type=event_type,
#             other_event_type=other_event_type,
#         )

#         # Add selected menu items
#         menu_item_ids = request.POST.getlist('menu_items')
#         menu_items = Menu.objects.filter(id__in=menu_item_ids)
#         event_plan.menu_items.set(menu_items)
#         event_plan.save()

#         # Handle optional catering service
#         if catering_service == 'yes':
#             Catering.objects.create(
#                 event=event_plan,
#                 event_type=event_type,
#                 amount=amount,  # Adjust if catering affects the amount
#                 advance_amount=advance_amount,
#                 payment_status='pending',
#             )

#         messages.success(request, 'Event plan submitted. We will contact you for confirmation.')
#         return redirect('event_history')

#     # Fetch Menu items for the template
#     menus = Menu.objects.all()
#     categories = Category.objects.all()  # Include categories for the dropdown
#     return render(request, 'management/plan_event.html', {'menus': menus, 'categories': categories})
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
import razorpay
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import EventPlan, Menu, Category, Customer, Staff, Payment, Catering

@login_required(login_url='/login/')  # Change to your desired login URL
def plan_event(request):
    if request.method == 'POST':
        try:
            event_date = request.POST.get('event_date')
            guest_count = int(request.POST.get('guest_count'))
            custom_dish = request.POST.get('custom_dish', '')
            amount_str = request.POST.get('amount', '0').strip()
            advance_amount_str = request.POST.get('advance_amount', '0').strip()

            # Validate and convert to Decimal
            amount = Decimal(amount_str) if amount_str else Decimal('0')
            advance_amount = Decimal(advance_amount_str) if advance_amount_str else Decimal('0')

            catering_service = request.POST.get('catering_service')
            event_type = request.POST.get('event_type')
            other_event_type = request.POST.get('other_event_type', '')

            # Create the event plan
            event_plan = EventPlan.objects.create(
                customer=request.user.customer_profile,
                guest_count=guest_count,
                custom_dish=custom_dish,
                event_date=event_date,
                amount=amount,
                advance_amount=advance_amount,
                payment_status='pending',
                event_type=event_type,
                other_event_type=other_event_type,
            )

            # Add selected menu items
            menu_item_ids = request.POST.getlist('menu_items')
            menu_items = Menu.objects.filter(id__in=menu_item_ids)
            event_plan.menu_items.set(menu_items)
            event_plan.save()

            # Handle optional catering service
            if catering_service == 'yes':
                Catering.objects.create(
                    event=event_plan,
                    event_type=event_type,
                    amount=amount,  # Adjust if catering affects the amount
                    advance_amount=advance_amount,
                    payment_status='pending',
                )

            # Store event_plan_id in the session
            request.session['event_plan_id'] = event_plan.id

            total_paise = int(advance_amount * 100)  # Convert to paise

            # Razorpay client initialization with SSL verification disabled
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET), verify=False)

            # Create a Razorpay Order
            razorpay_order = client.order.create({
                "amount": total_paise,
                "currency": "INR",
                "payment_capture": "1"
            })

            context = {
                'event_plan': event_plan,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'currency': 'INR',
                'advance_amount': advance_amount,
            }
            return render(request, 'management/confirm_payment_event.html', context)
        
        except (InvalidOperation, ValueError) as e:
            messages.error(request, f"An error occurred while processing your request: {e}")
            return redirect('plan_event')

    # Fetch Menu items and categories for the template
    menus = Menu.objects.all()
    categories = Category.objects.all()
    return render(request, 'management/plan_event.html', {'menus': menus, 'categories': categories})

@csrf_exempt
@login_required(login_url='/login/')  # Change to your desired login URL
def confirm_event_payment(request):
    if request.method == 'POST':
        # Razorpay payment details
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Verify payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET), verify=False)
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed.")
            return redirect('event_history')

        # Retrieve the event plan
        event_plan_id = request.session.get('event_plan_id')
        event_plan = get_object_or_404(EventPlan, id=event_plan_id)

        # Update event plan status
        event_plan.payment_status = 'completed'
        event_plan.save()

        # Create Payment instance
        Payment.objects.create(
            customer=request.user.customer_profile,
            service_type='event_plan',  # Event plan payment
            date=timezone.now(),
            amount=event_plan.advance_amount,
            method='online',
            status='completed',
        )

        messages.success(request, "Your event plan has been confirmed and payment completed!")
        return redirect('event_history')
    else:
        return redirect('event_history')

@login_required(login_url='/login/')  # Change to your desired login URL
def reservation_detail(request, reservation_id):
    reservation = get_object_or_404(TableReservation, id=reservation_id, customer=request.user.customer_profile)
    preorders = Preorder.objects.filter(reservation=reservation)
    return render(request, 'management/reservation_detail.html', {'reservation': reservation, 'preorders': preorders})

# Event History View
@login_required
def event_history(request):
    events = EventPlan.objects.filter(customer=request.user.customer_profile)
    return render(request, 'management/event_history.html', {'events': events})

@login_required(login_url='/login/')  # Change to your desired login URL
def event_detail(request, event_id):
    event = get_object_or_404(EventPlan, id=event_id, customer=request.user.customer_profile)
    return render(request, 'management/event_details.html', {'event': event})

from django.core.exceptions import ObjectDoesNotExist

def home(request):
    return render(request, 'management/home.html')

from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

@login_required(login_url='/login/')
def submit_feedback(request):
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        comments = request.POST.get('comments', '')

        if 1 <= rating <= 5:
            try:
                customer = request.user.customer_profile
            except ObjectDoesNotExist:
                customer = Customer.objects.create(user=request.user)
            
            Feedback.objects.create(
                customer=customer,
                rating=rating,
                comments=comments,
            )
            return redirect("home")
        else:
            return redirect("home")
    else:
        # If it's not a POST, you could return a simple response or a 405 error
        return HttpResponse("Invalid request method. Only POST is allowed.")

# Notification View
@login_required
def notifications(request):
    notifications = Notification.objects.filter(customer=request.user.customer_profile)
    return render(request, 'management/notifications.html', {'notifications': notifications})

def add_to_cart(request, menu_id):
    """Add an item to the cart and redirect to the cart page."""
    menu = get_object_or_404(Menu, id=menu_id)
    cart = request.session.get('cart', {})

    # Use menu_id as key (stringified) for session storage.
    key = str(menu_id)
    if key in cart:
        cart[key]['quantity'] += 1
    else:
        cart[key] = {
            'name': menu.name,
            'price': float(menu.price),  # convert Decimal if necessary
            'quantity': 1,
            'image': menu.image.url if menu.image else '',
        }
    request.session['cart'] = cart  # Save cart back to session

    return redirect('cart')  # This URL name should point to the cart page


def order_now(request, menu_id):
    """Add an item to the cart and redirect directly to the checkout page."""
    menu = get_object_or_404(Menu, id=menu_id)
    cart = request.session.get('cart', {})
    key = str(menu_id)
    if key in cart:
        cart[key]['quantity'] += 1
    else:
        cart[key] = {
            'name': menu.name,
            'price': float(menu.price),
            'quantity': 1,
            'image': menu.image.url if menu.image else '',
        }
    request.session['cart'] = cart

    return redirect('checkout')  # This URL name should point to the checkout page


def cart_view(request):
    """Display the contents of the cart with options to update or remove items."""
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    context = {'cart': cart, 'total': total}
    return render(request, 'management/cart.html', context)


def checkout_view(request):
    """Display a summary of the cart for checkout."""
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    context = {'cart': cart, 'total': total}
    return render(request, 'management/checkout.html', context)


def update_cart(request, menu_id):
    """Update the quantity of an item in the cart. Remove the item if quantity is 0."""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        key = str(menu_id)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

        if key in cart:
            if quantity > 0:
                cart[key]['quantity'] = quantity
            else:
                del cart[key]
            request.session['cart'] = cart

    return redirect('cart')
