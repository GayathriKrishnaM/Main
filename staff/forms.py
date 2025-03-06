from django import forms
from management.models import Staff
from django.contrib.auth.models import User

class DateInput(forms.DateInput):
    input_type = 'date'

class StaffRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = Staff
        fields = ['full_name', 'dob', 'place', 'city', 'pin', 'mobile', 'email', 'role']
        widgets = {
            'dob': DateInput()
        }
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data



class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['full_name', 'dob', 'place', 'city', 'pin', 'mobile', 'email', 'role']
