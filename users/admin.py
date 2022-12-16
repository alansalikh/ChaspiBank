from django.contrib import admin
from .models import User, Transaction, Deposit

class DepositAdmin(admin.ModelAdmin):
    list_display = ['user', 'cash', 'created', 'updated']

admin.site.register(Deposit, DepositAdmin)
admin.site.register(User)
admin.site.register(Transaction)

