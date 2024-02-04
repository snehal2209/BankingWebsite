from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from admins.models import *

class CustomerEditForm(forms.ModelForm):
    contact_number = forms.CharField(max_length=10)
    address = forms.CharField(max_length=100)
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'address', 'contact_number', 'date_of_birth']
   
class LoanStatusEditForm(forms.ModelForm):
    
    class Meta:
        model = Loan
        fields = ['status']
    
class UpdateLoanForm(forms.ModelForm):
    status = forms.ChoiceField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('closed', 'Closed')])
    class Meta:
        model = Loan
        fields = ['status']
    
     
class CustomerSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    contact_number = forms.CharField(max_length=10)
    address = forms.CharField(max_length=100)
    date_of_birth = forms.DateField()

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'contact_number', 'address', 'date_of_birth']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

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
    class Meta:
        model = Transaction
        fields = ['account_to', 'transaction_type', 'amount', 'description']




