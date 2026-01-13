from django.db import models
from django.utils import timezone
from inventory.models import Product  # <--- This import is ONLY valid here in sales.py

class Customer(models.Model):
    name = models.CharField(max_length=200, unique=True)

    # --- ADDED EMAIL FIELD ---
    email = models.EmailField(max_length=254, blank=True, null=True)
    # -------------------------

    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)

    def __str__(self): return self.name

class Order(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

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
