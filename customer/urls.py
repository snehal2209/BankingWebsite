from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    path('acc/', views.customer_acc, name='acc'),
    path('loan/', views.loan_application, name='loan'),
    path('pay_loan/', views.pay_loan, name='pay_loan'),
    path('deposit/', views.deposit, name='deposit'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('edit/', views.edit_customer_details, name='edit_customer_details'),
    path('transaction/', views.transaction_view, name='transaction'),
    #  path('create/', views.create_transaction, name='create_transaction'),
    path('success/<int:transaction_id>/', views.transaction_success, name='transaction_success'),
    path('update_deposit_status/', views.update_deposit_status, name='update_deposit_status'),

    
]

