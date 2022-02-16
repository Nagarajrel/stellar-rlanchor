from django.contrib import admin
from .models import Customer, CustomerStellarAccount
# Register your models here.

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'phone', 'first_name', 'last_name', 'bank_number', 'bank_account_number',
                    'bank_account_number')

class CustomerStellarAccount(admin.ModelAdmin):
    list_display = ('customer', 'stellar_account', 'muxed_account', 'memo', 'memo_type')


admin.site.register(Customer)
admin.site.register(CustomerStellarAccount)
