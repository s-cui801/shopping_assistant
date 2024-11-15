# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from datetime import datetime
from django.db import models


class Products(models.Model):
    product_id = models.AutoField(primary_key=True, blank=True)
    name = models.TextField()
    price = models.FloatField()
    stock = models.IntegerField()
    category = models.TextField()
    type = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products'

class Customers(models.Model):
    customer_id = models.AutoField(primary_key=True, blank=True)
    first_name = models.TextField()
    last_name = models.TextField()
    username = models.TextField()
    password = models.TextField()

    class Meta:
        managed = False
        db_table = 'customers'


class CartItems(models.Model):
    cart_item_id = models.AutoField(primary_key=True, blank=True)
    customer = models.ForeignKey(
        'Customers', 
        on_delete=models.CASCADE,
        db_column='customer_id',
        to_field='customer_id'
    )
    product = models.ForeignKey(
        'Products',
        on_delete=models.CASCADE,
        db_column='product_id',
        to_field='product_id'  # References the id field in Products table
    )
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cart_items'


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True, blank=True)
    customer = models.ForeignKey(
        'Customers', 
        on_delete=models.CASCADE,
        db_column='customer_id',
        to_field='customer_id'
        )
    order_status = models.TextField(default='Pending')
    payment_status = models.TextField()
    order_date = models.TextField(default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        managed = False
        db_table = 'orders'


class OrderItems(models.Model):
    order_item_id = models.AutoField(primary_key=True, blank=True)
    order = models.ForeignKey(
        'Orders', 
        on_delete=models.CASCADE,
        db_column='order_id',
        to_field='order_id'
        )
    product = models.ForeignKey(
        'Products', 
        on_delete=models.CASCADE,
        db_column='product_id', 
        to_field='product_id'
    )
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'order_items'
