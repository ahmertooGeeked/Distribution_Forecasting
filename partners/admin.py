from django.contrib import admin

from .models import Customer, Supplier

admin.site.register(Supplier)
admin.site.register(Customer)

# Register your models here.
