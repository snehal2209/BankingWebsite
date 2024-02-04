from django.db import models
import datetime
from django.contrib.auth.models import User
# Create your models here.
ROLE_CHOICES = (
    ('admin','admin'), 
    ('manager','manager'),
)

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    role = models.CharField(choices=ROLE_CHOICES,max_length=50)


 

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    contact_number = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    # pic = models.ImageField(upload_to='pic',blank=True, null=True)
    
    def __str__(self):
        return f"Customer ID: {self.customer_id}, Name: {self.first_name} {self.last_name}"




A_CHOICES = (
    ('active','active'), 
    ('frozen','frozen'),
    ('closed','closed'),
)

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=12, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=A_CHOICES, max_length=50)

    def save(self, *args, **kwargs):
        if not self.account_number:
            last_account = Account.objects.order_by('-account_id').first()
            if last_account:
                last_account_id = last_account.account_id
            else:
                last_account_id = 0
            new_account_id = last_account_id + 1
            self.account_number = f"68002209{new_account_id:04d}"
        super().save(*args, **kwargs)
        

T_CHOICES = (
    ('deposit','deposit'),
    ('withdrawal','withdrawal'),
    ('transfer','transfer'),
    ('LOAN','LOAN'),
    ('EMI','EMI'),
    ('FD','FD'),
    ('FD RETN','FD RETN'),
)
class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    account_number = models.ForeignKey(Account, on_delete=models.CASCADE)    
    account_to = models.CharField(max_length=12, blank=True, null=True) 
    transaction_type = models.CharField(choices=T_CHOICES, max_length=50)
    transaction_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField()
    


LOAN_CHOICES = (
    ('pending','pending'), 
    ('approved','approved'),
    ('rejected','rejected'),
    ('closed','closed'),
)
class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    loan_term = models.IntegerField()
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=LOAN_CHOICES, max_length=50)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)


FD_CHOICES = (
    ('active','active'), 
    ('matured','matured'),
    ('closed','closed'),
    ('req_stop','req_stop'),
)
class FixedDeposit(models.Model):
    deposit_id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    deposit_term = models.IntegerField()
    start_date = models.DateField()
    maturity_date = models.DateField()
    status = models.CharField(choices=FD_CHOICES, max_length=50)
    interest_earned = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

class Conversation(models.Model):
    conversation_id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    user_input = models.TextField()
    bot_response = models.TextField()
