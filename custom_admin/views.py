from django.shortcuts import render, redirect
from management.models import Customer, Category, Menu, TableReservation
from django.db import IntegrityError

def admin_dashboard(request):
    return render(request, 'admin_panel/dashboard.html')

def orders(request):
    return render(request, 'admin_panel/orders.html')

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "admin_panel/customers.html", {"customers": customers})

def reservations(request):
    return render(request, 'admin_panel/reservations.html')

def catering(request):
    return render(request, 'admin_panel/catering.html')

def menu_list(request):
    menus = Menu.objects.all()
    return render(request, 'admin_panel/menu_list.html', {'menus': menus})

def add_menu(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        unit = request.POST.get('unit')
        quantity = request.POST.get('quantity')
        discount = request.POST.get('discount') or 0.0  # Provide a default if needed
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        if not name or not price or not unit or not quantity or not category_id:
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
                quantity=quantity,
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

def reservations(request):
    reservations = TableReservation.objects.all()
    return render(request, 'admin_panel/reservations.html', {'reservations': reservations}) 

