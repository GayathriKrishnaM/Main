from django import forms
from management.models import Inventory, Customer, Menu, Category


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['menu', 'quantity', 'stock_alert_level']

        
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'dob', 'place', 'city', 'pin', 'mobile', 'email', 'user']
        
class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'price', 'unit', 'image', 'description', 'category']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
