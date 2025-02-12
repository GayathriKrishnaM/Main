from django.contrib import admin
from .models import Category,Ingredient,Menu,MenuVariant,MenuIngredient,Customer,Staff,Order,OrderItem,TableReservation,Preorder,EventPlan,Catering,Payment,Feedback,Notification

# Registering models with default ModelAdmin.
admin.site.register(Category)
admin.site.register(Ingredient)
admin.site.register(Menu)
admin.site.register(MenuVariant)
admin.site.register(MenuIngredient)
admin.site.register(Customer)
admin.site.register(Staff)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(TableReservation)
admin.site.register(Preorder)
admin.site.register(EventPlan)
admin.site.register(Catering)
admin.site.register(Payment)
admin.site.register(Feedback)
admin.site.register(Notification)
