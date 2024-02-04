from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from admins.models import *
import re
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomerEditForm(forms.ModelForm):
    contact_number = forms.CharField(max_length=10)
    address = forms.CharField(max_length=100)
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'address', 'contact_number', 'date_of_birth']
        
class CustomerSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    address = forms.CharField(max_length=100)
    date_of_birth = forms.DateField()
    contact_number = forms.IntegerField(
        validators=[
            MinValueValidator(1000000000, message="Contact number should be a 10-digit number."),
            MaxValueValidator(9999999999, message="Contact number should be a 10-digit number.")
        ]
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'contact_number', 'address', 'date_of_birth']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-Z]+$', first_name):
            raise forms.ValidationError("First name must contain only alphabets.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[a-zA-Z]+$', last_name):
            raise forms.ValidationError("Last name must contain only alphabets.")
        return last_name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        customer = Customer(
            username=user.username,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            contact_number=self.cleaned_data['contact_number'],
            address=self.cleaned_data['address'],
            date_of_birth=self.cleaned_data['date_of_birth'],
        )
        customer.save()
        return user
    
class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class TransactionForm(forms.ModelForm):
    description = forms.CharField()
    transaction_type = forms.CharField(initial='transfer')
    class Meta:
        model = Transaction
        fields = ['account_to', 'transaction_type', 'amount', 'description']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].widget.attrs['readonly'] = True

class LoanApplicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    interest_rate = forms.DecimalField(initial=7, disabled=True)
    class Meta:
        model = Loan
        fields = ['loan_amount', 'interest_rate', 'loan_term']
        
class FixedDepositForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['interest_rate'] = 5

    class Meta:
        model = FixedDeposit
        fields = ['deposit_amount', 'interest_rate', 'deposit_term']
        widgets = {
            'deposit_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control','readonly': 'readonly'}),
            'deposit_term': forms.NumberInput(attrs={'class': 'form-control'})
        }