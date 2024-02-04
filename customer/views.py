from django.shortcuts import render, redirect
from datetime import date, timedelta
from django.db.models import F, ExpressionWrapper, DecimalField, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from .forms import *
from decimal import Decimal
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.decorators import login_required
from admins.models import *
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError, ObjectDoesNotExist

# Create your views here.


def home_view(request):
    if request.user.is_anonymous:
        return redirect("/login")
    customer = Customer.objects.get(username=request.user.username)
    return render(request, 'customer/index.html',{'customer': customer})


def loan_application(request):
    customer = Customer.objects.get(username=request.user.username)
    account = Account.objects.get(customer_id=customer)
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.customer_id=customer
            loan.status = 'pending'  # Set default status
            loan.save()
            return redirect('/loan',{'done':'done'})  # Redirect to success page
    else:
        form = LoanApplicationForm()

    # return render(request, 'customer/loan_application.html', {'form': form})
    # loan = Loan.objects.filter(customer_id=customer.customer_id)
    loan = Loan.objects.filter(customer_id=customer.customer_id).annotate(total_amount=ExpressionWrapper(F('loan_amount') + (F('loan_amount') * F('interest_rate') * F('loan_term') / 100), output_field=DecimalField()))
    errors = form.errors.as_data() if form.errors else None
    return render(request, 'customer/loan_application.html', {'customer': customer, 'loans' : loan,'account' :account, 'form': form, 'errors': errors})

def deposit(request):
    customer = Customer.objects.get(username=request.user.username)
    account = Account.objects.get(customer_id=customer)
    form = FixedDepositForm()
    if request.method == 'POST':
        form = FixedDepositForm(request.POST)
        
        if form.is_valid():
            amount = form.cleaned_data['deposit_amount']
            try:
                if account.balance < amount:
                    raise ValidationError("Insufficient balance.")
            except ValidationError as e:
                error_message = str(e)
                return render(request, 'customer/deposit_applocation.html', {'form': form, 'error_message': error_message})
            fixed_deposit = form.save(commit=False)
            fixed_deposit.customer_id=customer
            fixed_deposit.start_date = date.today()  # Set start date as the form submission date
            fixed_deposit.maturity_date = fixed_deposit.start_date + timedelta(days=365 * fixed_deposit.deposit_term)  # Calculate maturity date by adding deposit term in years
            fixed_deposit.status="active"
            fixed_deposit.save()
            print(account.balance)
            account.balance=account.balance - amount
            account.save()
            done = "done"
            return redirect('/deposit', {'done':done})  # Redirect to a success page or list view
        else:
            # Form is not valid, display errors
            errors = form.errors.as_data()
            print(errors)
   
    
    deposits = FixedDeposit.objects.filter(customer_id=customer.customer_id)
    errors = form.errors.as_data() if form.errors else None
    return render(request, 'customer/deposit_applocation.html', {'customer': customer, 'deposits' : deposits, 'form': form, 'errors': errors})
    
from django.http import JsonResponse

def update_deposit_status(request):
    if request.method == 'POST':
        deposit_id = request.POST.get('deposit_id')
        print("deposit id =",deposit_id)
        # Perform any necessary validation or checks before updating the status
        # For example, you can fetch the deposit object from the database and update its status
        try:
            deposit = FixedDeposit.objects.get(deposit_id=deposit_id)
            deposit.status = 'req_stop'
            deposit.save()
            return redirect('/deposit')
        except FixedDeposit.DoesNotExist:
            return render(request, 'customer/deposit_applocation.html')
    else:
        return render(request, 'customer/deposit_applocation.html')

    
def pay_loan(request):
    customer = Customer.objects.get(username=request.user.username)
    account = Account.objects.get(customer_id=customer.customer_id)
    account_nm = account.account_number
    if request.method == 'POST':
        amount = Decimal(request.POST.get('loan_amount'))
        loan_id = request.POST.get('loan_id')
        transaction_type = 'EMI'
        description = "EMI paid"
        account_to = 9096634878
        loan = Loan.objects.get(loan_id=loan_id)
        try:
            transaction = create_transaction(account_nm, transaction_type, amount, description, account_to)
            # transaction_id=transaction.transaction_id
            loan.status="closed"
            loan.save()
            return redirect('/loan')
        except ValidationError as e:
            error_message = str(e)
            return render(request, 'customer/loan_application.html', {'error_message': error_message})
    return render(request, 'customer/loan_application.html')


# def home_view(request):
#     # if request.user.is_authenticated:
#     customer = Customer.objects.get(user=request.user)
#     # account = Account.objects.get(customer_id=customer_customerid)
#     context = {
#         'customer' : customer ,
#         # 'account': account,         
#     }
#     return render(request, 'customer/customer_home.html', context)
#     # return redirect('/login')
    
    # return render(request, "customer/customer_home.html", {'customer': customer}, {'account':account})



def signup_view(request):
    form = CustomerSignupForm()
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            customer = Customer.objects.get(username=user.username)

            # Create a new account for the customer
            account = Account.objects.create(
                customer_id=customer,
                balance=0,
                status='active'
            )
            
            return redirect('/login')
    return render(request, 'customer/signup.html', {'form': form})


# def signup_view(request):
#     if request.method == 'POST':
#         form = SignupForm(request.POST)
#         if form.is_valid():
#             # Create a new user
#             user = form.save()

#             # Create a new account for the user
#             account = Account.objects.create(
#                 customer_id=user,
#                 balance=0,
#                 status='active'
#             )

#             # Redirect to a success page or login page
#             return redirect('/login')
#     else:
#         form = SignupForm()

#     return render(request, 'customer/signup.html', {'form': form})


# def home_view(request):
#     customer_id = request.session.get('customer_id')
#     customer_username = request.session.get('customer_username')
#     print(customer_id)
#     return render(request, "customer/customer_home.html")


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            # messages.success(request,'Welcome!!')
            return redirect('/home')
        else:
            
            messages.warning(request,'Invalid username or password')
            return render(request, 'customer/customer_login.html')
    else:
        return render(request, 'customer/customer_login.html')

def customer_acc(request):
    print(request.user)
    customer = Customer.objects.get(username=request.user.username)
    account = Account.objects.get(customer_id=customer.customer_id)
    
    return render(request, 'customer/customer_acc.html',{'account': account,'customer':customer})

# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         try:
#             customer = Customer.objects.get(username=username)
#         except Customer.DoesNotExist:
#             customer = None
#         if customer is not None and customer.password == password:
#              # Display a login successful message
#             request.session['customer_id'] = customer.customer_id
#             request.session['customer_username'] = customer.username
#             global user_id
#             user_id=customer.customer_id
#             return redirect('/home')
#         error_message = 'Invalid username or password'
#         return render(request, 'customer/customer_login.html', {'error_message': error_message})
#     else:
#         return render(request, 'customer/customer_login.html')
        


def logout_view(request):
    logout(request)
    return redirect('/login')  #/login Redirect to the login page after logout

# def transaction_view(request):
#     if request.method == 'POST':
#         form = TransactionForm(request.POST)
#         if form.is_valid():
#             # transaction = form.save(commit=False)
#             # customer_customerid = request.session.get('customer_id')
#             # customer = Customer.objects.get(customer_id=customer_customerid)
#             # transaction.account_id = customer_id.account
#             transaction = form.save(commit=False)
#             customer = request.user.customer
#             transaction.account_id = customer.account
#             transaction.save()
#             return redirect('/home')  # Redirect to the home page after successful transaction
#     else:
#         form = TransactionForm()
    
#     context = {'form': form}
#     return render(request, 'customer/transaction.html', context)



def loan(request):
    customer_customerid = request.session.get('customer_id')
    customer_username = request.session.get('customer_username')
    print(customer_customerid)
    customer = Customer.objects.get(customer_id=customer_customerid) 
    return render(request, "customer/loans.html", {'customer': customer})

def delete_account(request):
    return render(request, "customer/delete_account.html")





def create_transaction(account_nm, transaction_type, amount, description, account_to=None):
    try:
        account = Account.objects.get(account_number=account_nm)
        print("account:-",account)
    except Account.DoesNotExist:
        raise ValidationError("Invalid account ID.")

    if amount == 0:
        raise ValidationError("Enter Valid Amount.")
    elif transaction_type == 'deposit':
        account.balance += amount
        account.save()
    elif transaction_type == 'withdrawal':
        if account.balance < amount:
            raise ValidationError("Insufficient balance.")
        account.balance -= amount
        account.save()
    else:
        if account.account_number == account_to:
            raise ValidationError("Cannot transfer to the same account.")

        try:
            destination_account = Account.objects.get(account_number=account_to)
        except Account.DoesNotExist:
            raise ValidationError("Invalid destination account number.")

        if account.balance < amount:
            raise ValidationError("Insufficient balance for transfer.")

        account.balance -= amount
        destination_account.balance += amount
        account.save()
        destination_account.save()
    # else:
    #     raise ValidationError("Invalid transaction type.")

    transaction = Transaction.objects.create(
        account_number=account,
        account_to=account_to,
        transaction_type=transaction_type,
        amount=amount,
        description=description
    )
    return transaction


def transaction_view(request):
    customer = Customer.objects.get(username=request.user.username)
    account = Account.objects.get(customer_id=customer.customer_id)
    account_nm = account.account_number
    if request.method == 'POST':
        
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction_type = form.cleaned_data['transaction_type']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            account_to = form.cleaned_data['account_to']
            try:
                transaction = create_transaction(account_nm, transaction_type, amount, description, account_to)
                # transaction_id=transaction.transaction_id
                return redirect('/transaction')
            except ValidationError as e:
                error_message = str(e)
                return render(request, 'customer/transaction.html', {'form': form,'customer':customer, 'error_message': error_message})
    else:
        form = TransactionForm()
    transactions = Transaction.objects.filter(Q(account_number=account) | Q(account_to=account_nm))
    return render(request, 'customer/transaction.html', {'form': form,'customer':customer, 'transactions' : transactions})

def transaction_success(request, transaction_id):
    transaction = Transaction.objects.get(transaction_id=transaction_id)
    return render(request, 'customer/transaction_success.html', {'transaction': transaction})


# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         print(username, password)
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('/home')  # Redirect to the home page after successful login
#         else:
#             error_message = 'Invalid username or password'
#             return render(request, 'customer/customer_login.html', {'error_message': error_message})
#     else:
#         error_message1 = 'user not valid'
#         return render(request, 'customer/customer_login.html', {'error_message1': error_message1})


def edit_customer_details(request):
    customer = Customer.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = CustomerEditForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('/home')
    else:
        form = CustomerEditForm(instance=customer)

    return render(request, 'customer/edit_customer.html', {'form': form})


# def edit_details(request):
#     if request.method == "POST":
#         # POST actions for BasicDetailsForms
#         try:
#             curr_user = Customer.objects.get(customer_id=request.session.get('customer_id'))
#             form = forms.CustomerForm(request.POST, instance=curr_user)
#             if form.is_valid():
#                 form.save()
#         except:
#             form = forms.CustomerForm(request.POST)
#             if form.is_valid():
#                 form = form.save(commit=False)
#                 form.user_name = request.user
#                 form.save()

#         # # POST actions for PresentLocationForm
#         # try:
#         #     curr_user = models.PresentLocation.objects.get(user_name=request.user)
#         #     form = forms.PresentLocationForm(request.POST, instance=curr_user)
#         #     if form.is_valid():
#         #         form.save()
#         # except:
#         #     form = forms.PresentLocationForm(request.POST)
#         #     if form.is_valid():
#         #         form = form.save(commit=False)
#         #         form.user_name = request.user
#         #         form.save()     
        
#         # POST actions for Password change
#         # form = PasswordChangeForm(request.user, request.POST)
#         # if form.is_valid():
#         #     user = form.save()
#         #     update_session_auth_hash(request, user)  # Important!
#         #     messages.success(request, 'Your password was successfully updated!')
#         #     return redirect('change_password')
#         # else:
#         #     messages.error(request, 'Please correct the error below.')

#         return redirect("customer/edit_details.html")
    
#     else: # GET actions
#         try:
#             curr_user = Customer.objects.get(user_name=request.user)
#             form1 = forms.CustomerForm(instance=curr_user) # basic details
#         except:
#             form1 = forms.CustomerForm()
        
#         # try:
#         #     curr_user = models.PresentLocation.objects.get(user_name=request.user)
#         #     form2 = forms.PresentLocationForm(instance=curr_user) # location
#         # except:
#         #     form2 = forms.PresentLocationForm()

#         # # change password
#         # form3 = PasswordChangeForm(request.user)

#         dici = {"form1": form1}
#         return render(request, "customer/edit_details.html", dici)