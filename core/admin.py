from django.contrib import admin

# Register your models here.
from .models import Customer, Transaction

admin.site.register(Customer)
admin.site.register(Transaction)