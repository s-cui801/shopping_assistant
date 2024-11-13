from django.contrib import admin
from .models import CartItems, Customers, Orders, Products, OrderItems

# Register your models here.

admin.site.register(Products)
admin.site.register(Customers)
admin.site.register(CartItems)
admin.site.register(Orders)
admin.site.register(OrderItems)