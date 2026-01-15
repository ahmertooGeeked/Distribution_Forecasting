from django.db import models
from django.utils import timezone
from inventory.models import Product  # Valid import here

class Customer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)

    def __str__(self): return self.name

class Order(models.Model):
    # --- SEPARATE STATUS CHOICES ---
    PAYMENT_CHOICES = [
        ('PENDING', 'Unpaid'),
        ('PAID', 'Paid'),
    ]
    DELIVERY_CHOICES = [
        ('PENDING', 'Processing'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # --- NEW FIELDS ---
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='PENDING')
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='PENDING')

    def __str__(self): return f"Order #{self.id} - {self.customer.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
