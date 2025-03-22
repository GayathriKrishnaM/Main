# staff/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from management.models import Staff, Catering, EventPlan, Order, Preorder, TableReservation, Customer # Import your Staff model
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .forms import StaffRegistrationForm, StaffProfileForm

@login_required
def dashboard(request):
    try:
        staff_obj = request.user.staff_profile
    except Staff.DoesNotExist:
        return redirect('error_page')
    
    role = staff_obj.role
    
    if role == 'manager':
        return manager_dashboard(request)
    elif role == 'chef':
        return chef_dashboard(request)
    elif role == 'waiter':
        return waiter_dashboard(request)
    elif role == 'other':
        return delivery_dashboard(request)
    else:
        # Handle unexpected roles
        return redirect('error_page')

def staff_register(request):
    if request.method == "POST":
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            # Create a new user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username=username, password=password)
            # Create the corresponding Staff profile
            staff = form.save(commit=False)
            staff.user = user
            staff.save()
            # Automatically authenticate and login the user
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('staff_dashboard')
    else:
        form = StaffRegistrationForm()
    return render(request, 'staff/staff_register.html', {'form': form})

def logout_and_redirect(request):
    logout(request)
    return redirect('staff_login')

@login_required
def profile(request):
    try:
        staff_obj = request.user.staff_profile
    except Staff.DoesNotExist:
        # Optionally, handle the case when no staff profile exists.
        return redirect('error_page')
    return render(request, 'staff/profile.html', {'staff': staff_obj})

@login_required
def edit_profile(request):
    try:
        staff_obj = request.user.staff_profile
    except Staff.DoesNotExist:
        return redirect('error_page')  # or a suitable page if profile not found

    if request.method == 'POST':
        form = StaffProfileForm(request.POST, instance=staff_obj)
        if form.is_valid():
            form.save()
            return redirect('staff_profile')  # Redirect to the profile view after saving
    else:
        form = StaffProfileForm(instance=staff_obj)
        
    return render(request, 'staff/edit_profile.html', {'form': form})

@login_required
def manager_dashboard(request):
    orders = Order.objects.all()
    reservations = TableReservation.objects.all()
    preorders = Preorder.objects.all()
    event_plans = EventPlan.objects.all()
    caterings = Catering.objects.all()
    staff_members = Staff.objects.all()

    context = {
        'orders': orders,
        'reservations': reservations,
        'preorders': preorders,
        'event_plans': event_plans,
        'caterings': caterings,
        'staff_members': staff_members,
    }
    return render(request, 'staff/manager_dashboard.html', context)

@login_required
def chef_dashboard(request):
    pending_orders = Order.objects.filter(order_status__in=['pending', 'confirmed'])
    preorders = Preorder.objects.filter(reservation__booking_status='confirmed')
    upcoming_events = EventPlan.objects.filter(event_date__gte=timezone.now())

    context = {
        'pending_orders': pending_orders,
        'preorders': preorders,
        'upcoming_events': upcoming_events,
    }
    return render(request, 'staff/chef_dashboard.html', context)

@login_required
def waiter_dashboard(request):
    reservations = TableReservation.objects.filter(booking_status='confirmed')

    context = {
        'reservations': reservations,
    }
    return render(request, 'staff/waiter_dashboard.html', context)

@login_required
def delivery_dashboard(request):
    order = Order.objects.all()
    return render(request, 'staff/other_dashboard.html', {'order': order})

from django.shortcuts import get_object_or_404, render

def view_orders(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'staff/view_orders.html', {'order': order})

def view_reservations(request, reservation_id):
    reservation = get_object_or_404(TableReservation, id=reservation_id)
    preorders = Preorder.objects.filter(reservation=reservation)
    
    return render(request, 'staff/view_reservations.html', {'reservation': reservation, 'preorders': preorders})

def view_event_plan(request, event_id):
    event_plans = get_object_or_404(EventPlan, id=event_id)
    caterings = Catering.objects.filter(event=event_plans)
    
    return render(request, 'staff/view_event_plan.html', {'event': event_plans, 'caterings': caterings})

def view_customers(request):
    customers = Customer.objects.all()
    return render(request, 'staff/view_customers.html', {'customers': customers})

def all_orders(request):
    orders = Order.objects.all()
    return render(request, 'staff/orders.html', {'orders': orders})

def all_reservations(request):
    reservations = TableReservation.objects.all()
    return render(request, 'staff/reservations.html', {'reservations': reservations})

def all_events(request):
    event = EventPlan.objects.all()
    return render(request, 'staff/events.html', {'event': event}) 

from django.shortcuts import get_object_or_404, redirect
from management.models import Order

def update_delivery_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        new_status = request.POST.get("delivery_status")
        order.delivery_status = new_status
        order.save()
    return redirect('staff_dashboard')  # Change to your actual staff dashboard URL name
