from django.shortcuts import get_object_or_404,render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta
from django.http import HttpRequest, HttpResponseRedirect
from .models import *
from .forms import *
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import F, ExpressionWrapper, DecimalField, Q
from django.utils.decorators import method_decorator
from .utils import get_plot




# Create your views here.
def index(request):
    status = Transaction.objects.all()
    customer = Customer.objects.all()
    customer_count = Customer.objects.count()
    account = Account.objects.all()
    loan = Loan.objects.all()
    context = {
        'status': status, 
        'customer' : customer,
        'account' : account,
        'loan' : loan,
        'customer_count' : customer_count,
    }
    return render(request, "admins/index.html",context)

def tables(request):
    status = Transaction.objects.all()
    customer = Customer.objects.all()
    customer_count = Customer.objects.count()
    account = Account.objects.all()
    loan = Loan.objects.all()
    deposit = FixedDeposit.objects.all()
    context = {
        'status': status, 
        'customer' : customer,
        'account' : account,
        'loan' : loan,
        'customer_count' : customer_count,
        'deposits' : deposit,
    }
    return render(request, "admins/tables.html",context)

def create_transaction(account_nm, transaction_type, amount, description, account_to=None):
    try:
        account = Account.objects.get(account_number=account_nm)
        print("account:-",account)
    except Account.DoesNotExist:
        raise ValidationError("Invalid account ID.")

    if transaction_type == 'deposit':
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

def update_loan(request):
    if request.method == 'POST':
        status = request.POST.get('status')
        loan_id = request.POST.get('loan_id')
        amount = Decimal(request.POST.get('loan_amount'))
        print("status and id ",status,"  ",loan_id)
        loan = Loan.objects.get(loan_id=loan_id)
        account = Account.objects.get(customer_id=loan.customer_id)
        bank_account = 9096634878
        print(bank_account)
        # update loan status in database
        
        if status == "approved":
            transaction_type = 'LOAN'
            
            description = 'Loan Distrubuted'
            account_to = account.account_number
            try:
                transaction = create_transaction(bank_account, transaction_type, amount, description, account_to)
                # transaction_id=transaction.transaction_id
                loan.start_date = date.today()  # Set start date as the form submission date
                loan.end_date = loan.start_date + timedelta(days=365 * loan.loan_term)
                loan.status = status
                loan.save()
                return redirect(reverse('admins:tables'))
            except ValidationError as e:
                error_message = str(e)
                return render(request, 'admins/tables.html', {'error_message': error_message})
            
            # if account.balance < amount:
            #     raise ValidationError("Insufficient balance for transfer.")
            # account.balance=account.balance + Decimal(amount)
            # account.save()
        loan.status = status
        loan.save()
        
        # redirect to a new page or update current page
        return redirect(reverse('admins:tables'),loan_id=loan_id)
        # return redirect('admins:tables', loan_id=loan_id)
    else:
        form = UpdateLoanForm()
    return render(request, '', {'form': form})

# def admin_home(request):
#     return render(request, "admins/admin_home.html")

def admin_login(request):
    return render(request, "admins/admin_login.html")

def customer_details(request):
    status = Customer.objects.all()
    context = {
        'status': status,   
    }
    return render(request, 'admins/customer_details.html', context)

def account_details(request):
    status = Account.objects.all()
    customer = Customer.objects.all()
    context = {
        'status': status, 
        'customer' : customer ,
    }
    return render(request, 'admins/account_details.html', context)

def transaction_details(request):
    status = Transaction.objects.all()
    customer = Customer.objects.all()
    account = Account.objects.all()
    context = {
        'status': status, 
        'customer' : customer,
        'account' : account,
    }
    return render(request, 'admins/transaction_details.html', context)

def plot(request):
    status = Transaction.objects.all()
    customer = Customer.objects.all()
    account = Account.objects.all()
    x = [x.selling_price for x in qs]
    y = [y.discounted_price for y in qs]
    chart = get_plot(x,y)
    context = {
        'status': status, 
        'customer' : customer,
        'account' : account,
        'chart':chart
    }
    return render(request, 'admins/plot.html', context)





def fd_details(request, pk):
    fd = get_object_or_404(FixedDeposit, pk=pk)
    customer = get_object_or_404(Customer, pk=fd.customer_id.customer_id)
    deposit_amount1 = fd.deposit_amount
    interest_rate1 = fd.interest_rate
    deposit_term1 = fd.deposit_term

    # Simple Interest Formula: (deposit_amount * interest_rate * deposit_term) / 100
    simple_interest = (deposit_amount1 * interest_rate1 * deposit_term1) / 100
    simple_interest = round(simple_interest, 2) 

    # Total Amount Formula: deposit_amount + simple_interest
    total_amount = deposit_amount1 + simple_interest
    total_amount = round(total_amount, 2) 
    
    account = Account.objects.get(customer_id=fd.customer_id)
    account_to = account.account_number
    if request.method == 'POST':
        print(account_to)
        amount = Decimal(total_amount)
        transaction_type = 'FD RETN'
        description = "FD RETURN"
        account_nm = 9096634878
        fd1 = FixedDeposit.objects.get(deposit_id=pk)
        try:
            transaction = create_transaction(account_nm, transaction_type, amount, description, account_to)
            # transaction_id=transaction.transaction_id
            fd1.status="closed"
            fd1.save()
            return redirect(reverse('admins:tables'))
        except ValidationError as e:
            error_message = str(e)
            return render(request, 'admins/tables.html', {'error_message': error_message})
        
    return render(request, 'admins/fd_details.html', {'fd': fd, 'customer':customer, 'simple_interest':simple_interest, 'total_amount':total_amount})


    