from django.contrib import admin
from .models import *
# Register your models here.



admin.site.register(Admin)
admin.site.register(Customer)
admin.site.register(Transaction)
admin.site.register(Account)
admin.site.register(Loan)
admin.site.register(FixedDeposit)
admin.site.register(Conversation)