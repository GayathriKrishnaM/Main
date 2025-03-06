from django import forms
from management.models import Inventory, Customer, Menu, Category


class DateInput(forms.DateInput):
    input_type = 'date'
    
class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['menu', 'quantity', 'original_quantity', 'expiry_date', 'stock_alert_level']
        widgets = {
            'expiry_date': DateInput(),
        }
        
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'dob', 'place', 'city', 'pin', 'mobile', 'email', 'user']
        
class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'price', 'unit', 'image', 'discount', 'description', 'category']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
