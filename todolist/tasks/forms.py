from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Task
import re


class CustomUserCreationForm(UserCreationForm):
    """Registration form with custom validation for password and phone number."""
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number (e.g., +12345678901)',
            'type': 'tel'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'phone_number', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
                'autocomplete': 'username'
            })
        }
    
    def clean_password1(self):
        """Validate password meets requirements."""
        password = self.cleaned_data.get('password1')
        
        if not password:
            raise forms.ValidationError('Password is required.')
        
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        
        if not re.search(r'\d', password):
            raise forms.ValidationError('Password must contain at least one number.')
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            raise forms.ValidationError('Password must contain at least one special character.')
        
        return password
    
    def clean_phone_number(self):
        """Validate phone number format and uniqueness."""
        phone = self.cleaned_data.get('phone_number')
        
        if not re.match(r'^\+?1?\d{9,15}$', phone):
            raise forms.ValidationError('Phone number must be 9-15 digits, optionally starting with + or 1.')
        
        if CustomUser.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError('This phone number is already registered.')
        
        return phone
    
    def clean(self):
        """Ensure passwords match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data


class CustomAuthenticationForm(AuthenticationForm):
    """Login form using phone number instead of username."""
    username = forms.CharField(
        label='Phone Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number',
            'autocomplete': 'tel',
            'type': 'tel'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def clean_username(self):
        """Validate that phone number exists."""
        phone = self.cleaned_data.get('username')
        
        if phone:
            try:
                user = CustomUser.objects.get(phone_number=phone)
                return user.username  # Return username for authentication
            except CustomUser.DoesNotExist:
                raise forms.ValidationError('User not found with this phone number.')
        
        return phone


class TaskForm(forms.ModelForm):
    """Form for creating and updating tasks."""
    class Meta:
        model = Task
        fields = ('title', 'description', 'due_date')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Task Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Task Description (optional)',
                'rows': 3
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
    
    def clean_due_date(self):
        """Ensure due date is not in the past."""
        from django.utils import timezone
        due_date = self.cleaned_data.get('due_date')
        
        if due_date and due_date < timezone.now().date():
            raise forms.ValidationError('Cannot add tasks to dates in the past.')
        
        return due_date
