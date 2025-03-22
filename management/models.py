from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

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
        ('delivery boy', 'Delivery Boy'),
    ]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_profile')
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.full_name} ({self.role})"



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Menu(models.Model):
    name = models.CharField(max_length=100, default='Dish Name')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    image = models.ImageField(upload_to='menu_images/', default='menu_images/default.jpg')
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menus')
    # inventory = models.OneToOneField('Inventory', on_delete=models.CASCADE, null=True, blank=True, related_name='menu_inventory')

    def __str__(self):
        return self.name

from django.core.validators import MinValueValidator
from datetime import date, timedelta

class Inventory(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='inventories')
    quantity = models.IntegerField()
    original_quantity = models.IntegerField(default=0) # Add this field
    expiry_date = models.DateField()
    stock_alert_level = models.FloatField(default=0, help_text="Alert level quantity.")
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.pk is None:  # If this is a new inventory item
            self.original_quantity = self.quantity
            if not self.expiry_date:  # Only set expiry date if it's not already provided
                self.expiry_date = date.today()

        # Automatically deactivate expired items (only if the expiry date is *before* today)
        self.is_active = self.expiry_date >= date.today()

        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.menu.name}  {self.quantity}"

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
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='confirmed')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} x {self.menu}"

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
    date_time = models.DateTimeField(default=timezone.now)
    booking_status = models.CharField(max_length=20, choices=RESERVATION_STATUS_CHOICES, default='pending')
    booking_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Reservation {self.id} for {self.customer.full_name}"

    def clean(self):
        if self.date < date.today():
            raise ValidationError("Reservation date cannot be in the past.")
        
        if self.guest_count < 1 or self.guest_count > 12:
            raise ValidationError("Guest count should be less than 13.")
        
        def save(self, *args, **kwargs):
            self.clean()
            super().save(*args, **kwargs)
            
    def can_cancel(self):
        return (timezone.now() - self.date_time) < timezone.timedelta(hours=24)

            
class Preorder(models.Model):
    reservation = models.ForeignKey(TableReservation, related_name='preorders', on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} {self.menu} for Reservation {self.reservation.id}"

from datetime import datetime

class EventPlan(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    EVENT_TYPE_CHOICES = [
        ('marriage', 'Marriage'),
        ('birthday', 'Birthday'),
        ('reception', 'Reception'),
        ('others', 'Others'),
    ]

    EVENT_STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    menu_items = models.ManyToManyField(Menu, blank=True)
    custom_dish = models.CharField(max_length=255, blank=True, help_text="Custom dish if any")
    guest_count = models.PositiveIntegerField(default=0)
    booking_date_time = models.DateTimeField(default=timezone.now, help_text="Booking datetime")
    event_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='others')
    other_event_type = models.CharField(max_length=255, blank=True, help_text="Specify if event type is others")
    status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES, default='planned')
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, help_text="Staff handling the event")

    def __str__(self):
        return f"Event {self.id} for {self.customer.full_name}"

    def save(self, *args, **kwargs):
        """Ensure event date is at least 5 days from today"""
        if isinstance(self.event_date, str):  # Convert to date object if needed
            self.event_date = datetime.strptime(self.event_date, "%Y-%m-%d").date()

        if self.event_date < (timezone.now().date() + timedelta(days=5)):
            raise ValueError("Event date must be at least 5 days from today.")
        
        super().save(*args, **kwargs)

    def can_cancel(self):
        """Allow cancellation only if today is at least 2 days before the event."""
        return timezone.now().date() < (self.event_date - timedelta(days=2))


class Catering(models.Model):
    EVENT_STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    event = models.OneToOneField(EventPlan, on_delete=models.CASCADE, related_name='catering')
    counter_design = models.CharField(max_length=100, blank=True)
    plate_type = models.CharField(max_length=100, blank=True)
    custom_option = models.CharField(max_length=255, blank=True, help_text="Custom idea if any")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Feedback #{self.id} from {self.customer.full_name}"

class Notification(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    message = models.TextField()
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notification #{self.id} for {self.customer.full_name}"
