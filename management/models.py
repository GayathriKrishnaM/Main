from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Person(models.Model):
    full_name = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)
    place = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    pin = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.full_name

class Customer(Person):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.full_name

class Staff(Person):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('chef', 'Chef'),
        ('waiter', 'Waiter'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_profile')
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.full_name} ({self.role})"



class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    quantity = models.FloatField(validators=[MinValueValidator(0)])
    original_quantity = models.FloatField(validators=[MinValueValidator(0)])
    expiry_date = models.DateField(null=True, blank=True)
    stock_alert_level = models.FloatField(default=0, help_text="Alert level quantity.")

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Menu(models.Model):
    name = models.CharField(max_length=100, default='Dish Name')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='menu_images/', default='menu_images/default.jpg')
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menus')

    def __str__(self):
        return self.name

class MenuVariant(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='variants')
    variant_name = models.CharField(max_length=100, help_text="Variant e.g. Chicken, Fish, Vegetable")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='menu_variant_images/', null=True, blank=True)
    additional_description = models.TextField(blank=True)

    class Meta:
        unique_together = ('menu', 'variant_name')

    def __str__(self):
        return f"{self.menu.dish_name} - {self.variant_name}"

class MenuIngredient(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_required = models.FloatField(validators=[MinValueValidator(0)], default=0,
                                          help_text="Quantity of ingredient used in dish")

    def __str__(self):
        return f"{self.ingredient.name} in {self.menu.dish_name}"

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    DELIVERY_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True,
                              help_text="Staff member handling the order")
    date_time = models.DateTimeField(default=timezone.now)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_variant = models.ForeignKey(MenuVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} x {self.menu_variant}"

class TableReservation(models.Model):
    RESERVATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    table_id = models.CharField(max_length=20, help_text="Identifier for the table")
    guest_count = models.PositiveIntegerField(default=1)
    date = models.DateField()
    time = models.TimeField()
    booking_status = models.CharField(max_length=20, choices=RESERVATION_STATUS_CHOICES, default='pending')
    booking_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Reservation {self.id} for {self.customer.full_name}"

class Preorder(models.Model):
    reservation = models.ForeignKey(TableReservation, related_name='preorders', on_delete=models.CASCADE)
    menu_variant = models.ForeignKey(MenuVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menu_variant} for Reservation {self.reservation.id}"

class EventPlan(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    menu_items = models.ManyToManyField(MenuVariant, blank=True)
    custom_dish = models.CharField(max_length=255, blank=True, help_text="Custom dish if any")
    guest_count = models.PositiveIntegerField(default=0)
    booking_date_time = models.DateTimeField(default=timezone.now, help_text="Booking datetime")
    event_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True,
                              help_text="Staff handling the event")

    def __str__(self):
        return f"Event {self.id} for {self.customer.full_name}"

class Catering(models.Model):
    EVENT_STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    event = models.OneToOneField(EventPlan, on_delete=models.CASCADE, related_name='catering')
    event_type = models.CharField(max_length=100, help_text="Type of event")
    counter_design = models.CharField(max_length=100, blank=True)
    plate_type = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=EventPlan.PAYMENT_STATUS_CHOICES, default='pending')
    status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES, default='planned')

    def __str__(self):
        return f"Catering for Event {self.event.id}"

class Payment(models.Model):
    SERVICE_CHOICES = [
        ('order', 'Order'),
        ('reservation', 'Reservation'),
        ('event', 'Event'),
        ('catering', 'Catering'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online', 'Online'),
        ('other', 'Other'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, help_text="Payment method")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Payment #{self.id} by {self.customer.full_name}"

class Feedback(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comments = models.TextField(blank=True)
    reply = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Feedback #{self.id} from {self.customer.full_name}"

class Notification(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    message = models.TextField()
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notification #{self.id} for {self.customer.full_name}"
