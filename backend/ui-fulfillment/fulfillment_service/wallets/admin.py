from django.contrib import admin

from .models import Transaction, Wallet

admin.site.register(Wallet)
admin.site.register(Transaction)
