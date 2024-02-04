
from django.urls import path
from . import views

app_name = 'admins'

urlpatterns = [
    path('', views.index, name='admin_index'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('customer_details/', views.customer_details, name='customer_details'),
    path('account_details/', views.account_details, name='account_details'),
    path('transaction_details/', views.transaction_details, name='transaction_details'),
    path('update-loan/', views.update_loan, name='update-loan'),
    path('plot/', views.plot, name='plot'),
    path('tables/', views.tables, name='tables'),
    path('fd_details/<int:pk>/', views.fd_details, name='fd_details'),
]
