from django.shortcuts import render, redirect, get_object_or_404
from management.models import Customer, Category, Menu, TableReservation, EventPlan, Staff, Order, Inventory, Preorder, Feedback, Notification, Payment
from django.db import IntegrityError
from staff.forms import StaffProfileForm  # Import the form from the staff app
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
from django.contrib.auth.models import User
from .models import AdminInvitation
from django.contrib import messages

def admin_required(view_func):
    decorated_view_func = user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url='custom_admin:admin_login'
    )(view_func)
    return decorated_view_func

@admin_required
def admin_profile(request):
    return render(request, 'admin_panel/admin_profile.html')

@admin_required
def admin_logout(request):
    logout(request)
    return redirect('custom_admin:admin_login')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('custom_admin:admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'admin_panel/admin_login.html')


def admin_register(request):
    if request.method == 'POST':
        invitation_code = request.POST.get('invitation_code')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validate the invitation
        try:
            invitation = AdminInvitation.objects.get(code=invitation_code, email=email, used=False)
        except AdminInvitation.DoesNotExist:
            messages.error(request, 'Invalid or expired invitation code.')
            return render(request, 'admin_panel/admin_register.html')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'admin_panel/admin_register.html')

        # Create the admin user
        user = User.objects.create_user(username=username, password=password, email=email, is_staff=True)

        # Authenticate the user to set the backend attribute
        user = authenticate(username=username, password=password)

        if user is not None:
            # Mark the invitation as used
            invitation.used = True
            invitation.save()

            # Log the user in
            login(request, user)
            messages.success(request, 'Admin account created successfully.')
            return redirect('custom_admin:admin_dashboard')
        else:
            messages.error(request, 'Authentication failed. Please try again.')
            return render(request, 'admin_panel/admin_register.html')

    return render(request, 'admin_panel/admin_register.html')


@admin_required
def admin_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Important to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('custom_admin:admin_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'admin_panel/admin_change_password.html', {'form': form})

# from datetime import timedelta
# from decimal import Decimal
# from django.db.models import Sum
# from django.utils import timezone
# from django.shortcuts import render

# @admin_required
# def admin_dashboard(request):
#     # Calculate today's date range
#     today = timezone.now().date()
#     month_start = today.replace(day=1)
    
#     # Today's revenue and orders
#     daily_data = Order.objects.filter(date_time__date=today)
#     daily_orders = daily_data.count()
    
#     # Monthly revenue and orders
#     monthly_data = Order.objects.filter(date_time__date__gte=month_start)
#     monthly_orders = monthly_data.count()

#     # Revenue from events and table reservations
#     event_revenue = EventPlan.objects.filter(event_date__gte=month_start).aggregate(total=Sum('advance_amount'))['total'] or 0
#     reservation_revenue = TableReservation.objects.filter(date__gte=month_start).aggregate(total=Sum('booking_fee'))['total'] or 0
#     order_revenue = Order.objects.filter(date_time__date__gte=month_start).aggregate(total=Sum('total_amount'))['total'] or 0
    
#     # Total revenue
#     monthly_revenue = order_revenue + event_revenue + reservation_revenue

#     # Get filtered data for today
#     daily_order = Order.objects.filter(date_time__date=today)
#     daily_event = EventPlan.objects.filter(booking_date_time__date=today)
#     daily_reservation = TableReservation.objects.filter(date_time__date=today)

#     # Calculate revenue
#     daily_revenue = (
#         daily_order.aggregate(total=Sum('total_amount'))['total'] or 0
#     ) + (
#         daily_event.aggregate(total=Sum('advance_amount'))['total'] or 0
#     ) + (
#         daily_reservation.aggregate(total=Sum('booking_fee'))['total'] or 0
#     )

#     # Active staff count
#     active_staff = Staff.objects.filter(user__is_active=True).count()
#     available_staff = Staff.objects.filter(user__is_active=True).count()
    
#     # Recent orders
#     orders = Order.objects.all().order_by('-date_time')[:10]
#     reservations = TableReservation.objects.all().order_by('-date')[:10]
#     events = EventPlan.objects.all().order_by('-event_date')[:10]
    
#     # Chart data (example)
#     last_seven_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
#     chart_labels = [day.strftime('%b %d') for day in last_seven_days]
#     chart_data = []
#     for day in last_seven_days:
#         total = Order.objects.filter(date_time__date=day).aggregate(total=Sum('total_amount'))['total'] or 0
#         chart_data.append(float(total))
    
#     context = {
#         'daily_revenue': daily_revenue,
#         'daily_orders': daily_orders,
#         'monthly_revenue': monthly_revenue,
#         'monthly_orders': monthly_orders,
#         'order_revenue': order_revenue,
#         'event_revenue': event_revenue,
#         'reservation_revenue': reservation_revenue,
#         'active_staff': active_staff,
#         'available_staff': available_staff,
#         'orders': orders,
#         'reservations': reservations,
#         'events': events,
#         'chart_labels': chart_labels,
#         'chart_data': chart_data,
#     }
#     return render(request, 'admin_panel/dashboard.html', context)
from datetime import datetime, timedelta
from django.utils.timezone import make_aware, now
from django.db.models import Sum
from django.shortcuts import render
from management.models import Order, EventPlan, TableReservation, Staff  # Ensure models are imported

@admin_required
def admin_dashboard(request):
    # Get the current time and date
    today = now().date()
    
    # Get start of the month (timezone-aware)
    month_start = make_aware(datetime.combine(today.replace(day=1), datetime.min.time()))

    # Get start of today (timezone-aware)
    today_start = make_aware(datetime.combine(today, datetime.min.time()))
    
    # Get today's orders and revenue
    daily_orders = Order.objects.filter(date_time__gte=today_start).count()
    daily_revenue = (
        Order.objects.filter(date_time__gte=today_start).aggregate(total=Sum('total_amount'))['total'] or 0
    ) + (
        EventPlan.objects.filter(booking_date_time__gte=today_start).aggregate(total=Sum('advance_amount'))['total'] or 0
    ) + (
        TableReservation.objects.filter(date_time__gte=today_start).aggregate(total=Sum('booking_fee'))['total'] or 0
    )

    # Get monthly orders and revenue
    monthly_orders = Order.objects.filter(date_time__gte=month_start).count()
    order_revenue = Order.objects.filter(date_time__gte=month_start).aggregate(total=Sum('total_amount'))['total'] or 0
    event_revenue = EventPlan.objects.filter(event_date__gte=month_start).aggregate(total=Sum('advance_amount'))['total'] or 0
    reservation_revenue = TableReservation.objects.filter(date__gte=month_start).aggregate(total=Sum('booking_fee'))['total'] or 0
    monthly_revenue = order_revenue + event_revenue + reservation_revenue

    # Active staff count
    active_staff = Staff.objects.filter(user__is_active=True).count()

    # Recent orders, reservations, and events
    orders = Order.objects.select_related('customer', 'staff').order_by('-date_time')[:10]
    reservations = TableReservation.objects.order_by('-date')[:10]
    events = EventPlan.objects.order_by('-event_date')[:10]

    # Chart data for the last 7 days


    # Generate last 7 days
    last_seven_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    chart_labels = [day.strftime('%b %d') for day in last_seven_days]

    # Fetch revenue data with a proper date range
    chart_data = []
    for day in last_seven_days:
        start_of_day = make_aware(datetime.combine(day, datetime.min.time()))  # 00:00:00
        end_of_day = make_aware(datetime.combine(day, datetime.max.time()))  # 23:59:59

        total_revenue = Order.objects.filter(date_time__range=(start_of_day, end_of_day)).aggregate(total=Sum('total_amount'))['total'] or 0
        chart_data.append(float(total_revenue))


    # Context for template
    context = {
        'daily_revenue': daily_revenue,
        'daily_orders': daily_orders,
        'monthly_revenue': monthly_revenue,
        'monthly_orders': monthly_orders,
        'order_revenue': order_revenue,
        'event_revenue': event_revenue,
        'reservation_revenue': reservation_revenue,
        'active_staff': active_staff,
        'orders': orders,
        'reservations': reservations,
        'events': events,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from management.models import Customer
from .forms import CustomerForm

@admin_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "admin_panel/customers.html", {"customers": customers})

@admin_required
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:admin_customers')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'admin_panel/edit_customer.html', {'form': form})

@admin_required
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('custom_admin:admin_customers')
    return render(request, 'admin_panel/customer_list.html', {'customer': customer})

@admin_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'admin_panel/add_customer.html', {'form': form})

@admin_required
def reservations(request):
    return render(request, 'admin_panel/reservations.html')

@admin_required
def catering(request):
    return render(request, 'admin_panel/catering.html')

@admin_required
def menu_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        menus = Menu.objects.filter(name__icontains=search_query)
    else:
        menus = Menu.objects.all()
    return render(request, 'admin_panel/menu_list.html', {'menus': menus})

@admin_required
def add_menu(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        unit = request.POST.get('unit')
        discount = request.POST.get('discount') or 0.0  # Provide a default if needed
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        if not name or not price or not unit or not category_id:
            error = "Please fill in all required fields."
            categories = Category.objects.all()
            return render(request, 'admin_panel/add_menu.html', {'error': error, 'categories': categories})

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            error = "Invalid category selected."
            categories = Category.objects.all()
            return render(request, 'admin_panel/add_menu.html', {'error': error, 'categories': categories})

        try:
            Menu.objects.create(
                name=name,
                price=price,
                unit=unit,
                discount=discount,
                description=description,
                category=category,
                image=image
            )
            return redirect('custom_admin:menu_list')  # Use the namespaced URL
        except IntegrityError as e:
            error = f"An error occurred: {str(e)}"
            categories = Category.objects.all()
            return render(request, 'admin_panel/add_menu.html', {'error': error, 'categories': categories})

    categories = Category.objects.all()
    return render(request, 'admin_panel/add_menu.html', {'categories': categories})

@admin_required
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')

        if not category_name:
            error = "Please provide a category name."
            return render(request, 'admin_panel/add_category.html', {'error': error})

        # Check if the category already exists
        if not Category.objects.filter(name=category_name).exists():
            Category.objects.create(name=category_name)
            return redirect('custom_admin:add_menu')  # Redirect to the add_menu page

        else:
            error = "Category with this name already exists."
            return render(request, 'admin_panel/add_category.html', {'error': error})

    return render(request, 'admin_panel/add_category.html')

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'admin_panel/category_list.html', {'categories': categories})

from .forms import CategoryForm

@admin_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_panel/edit_category.html', {'form': form})

@admin_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('custom_admin:category_list')
    return render(request, 'admin_panel/category_list.html')

from django.shortcuts import render, get_object_or_404, redirect
from management.models import Inventory, Menu
from .forms import InventoryForm

@admin_required
def inventory_list(request):
    inventory_items = Inventory.objects.all()
    return render(request, 'admin_panel/inventory_list.html', {'inventory_items': inventory_items})

@admin_required
def add_inventory(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:inventory_list')
    else:
        form = InventoryForm()
    return render(request, 'admin_panel/add_inventory.html', {'form': form})

@admin_required
def edit_inventory(request, pk):
    inventory_item = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory_item)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:inventory_list')
    else:
        form = InventoryForm(instance=inventory_item)
    return render(request, 'admin_panel/edit_inventory.html', {'form': form})


@admin_required
def reservations(request):
    reservations = TableReservation.objects.all()
    return render(request, 'admin_panel/reservations.html', {'reservations': reservations}) 

@admin_required
def events(request):
    events = EventPlan.objects.all()
    return render(request, 'admin_panel/catering.html', {'events': events}) 

@admin_required
def staff_list(request):
    staffs = Staff.objects.all()
    return render(request, 'admin_panel/staff_list.html', {'staffs': staffs})

@admin_required
def staff_detail(request):
    staff = Staff.objects.all()
    return render(request, 'admin_panel/staff_detail.html', {'staff': staff})

@admin_required
def staff_edit(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        form = StaffProfileForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:staff_list')
    else:
        form = StaffProfileForm(instance=staff)
    return render(request, 'admin_panel/staff_edit.html', {'form': form})

@admin_required
def staff_delete(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.delete()
        return redirect('custom_admin:staff_list')
    return render(request, 'admin_panel/staff_list.html')

from staff.forms import StaffRegistrationForm  # Assuming you have a form for Staff

@admin_required
def add_staff(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:staff_list')
    else:
        form = StaffRegistrationForm()
    return render(request, 'admin_panel/add_staff.html', {'form': form})

@admin_required
def view_orders(request):
    orders = Order.objects.all()
    return render(request, 'admin_panel/orders.html', {'orders': orders})

from .forms import MenuForm

@admin_required
def edit_menu(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        form = MenuForm(request.POST, request.FILES, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:menu_list')
    else:
        form = MenuForm(instance=menu)
    return render(request, 'admin_panel/edit_menu.html', {'form': form})

@admin_required
def delete_menu(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        menu.delete()
        return redirect('custom_admin:menu_list')
    return render(request, 'admin_panel/menu_list.html', {'menu': menu})

@admin_required
def view_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'admin_panel/view_order.html', {'order': order})

@admin_required
def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.order_status = request.POST.get('order_status')
        order.payment_status = request.POST.get('payment_status')
        order.delivery_status = request.POST.get('delivery_status')
        order.save()
        return redirect('custom_admin:view_order', pk=pk)
    return render(request, 'admin_panel/edit_order.html', {'order': order})

@admin_required
def view_reservation(request, pk):
    reservation = get_object_or_404(TableReservation, id=pk)
    preorders = Preorder.objects.filter(reservation=reservation)
    return render(request, 'admin_panel/view_reservation.html', {'reservation': reservation, 'preorders': preorders})

@admin_required
def edit_reservation(request, pk):
    reservation = get_object_or_404(TableReservation, pk=pk)
    if request.method == 'POST':
        reservation.booking_status = request.POST.get('booking_status')
        reservation.payment_status = request.POST.get('payment_status')
        reservation.save()
        return redirect('custom_admin:view_reservation', pk=pk)
    return render(request, 'admin_panel/edit_reservation.html', {'reservation': reservation})

@admin_required
def view_event(request, pk):
    event = get_object_or_404(EventPlan, pk=pk)
    return render(request, 'admin_panel/view_event.html', {'event': event})

@admin_required
def edit_event(request, pk):
    event = get_object_or_404(EventPlan, pk=pk)
    if request.method == 'POST':
        event.event_type = request.POST.get('event_type')
        event.status = request.POST.get('status')
        event.payment_status = request.POST.get('payment_status')
        event.save()
        return redirect('custom_admin:view_event', pk=pk)
    return render(request, 'admin_panel/edit_event.html', {'event': event})

@admin_required
def view_feedback(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'admin_panel/view_feedback.html', {'feedbacks': feedbacks})

@admin_required
def view_notification(request):
    notifications = Notification.objects.all()
    return render(request, 'admin_panel/view_notification.html', {'notifications': notifications})

@admin_required
def view_payment(request):
    payments = Payment.objects.all()
    return render(request, 'admin_panel/view_payment.html', {'payments': payments})