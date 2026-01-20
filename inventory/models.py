from django.db import models
from django.utils import timezone

# ============================
# 1. CATEGORY
# ============================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self): return self.name

# ============================
# 2. PRODUCT
# ============================
class Product(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'Pieces (pcs)'),
        ('kg', 'Kilogram (kg)'),
        ('ltr', 'Liter (L)'),
        ('box', 'Box'),
        ('m', 'Meter (m)'),
        ('doz', 'Dozen'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.CharField(max_length=5, choices=UNIT_CHOICES, default='pcs')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} ({self.stock_quantity} {self.unit})"

# ============================
# 3. SUPPLIER & PO
# ============================
class Supplier(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    def __str__(self): return self.name

class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_ordered = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.total_cost = self.unit_cost * self.quantity
        super().save(*args, **kwargs)

# ============================
# 4. SYSTEM SETTINGS (UPDATED)
# ============================
class SystemSettings(models.Model):
    currency_symbol = models.CharField(max_length=5, default='$')

    # --- NEW: Theme Field ---
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
    ]
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')

    def __str__(self):
        return "System Settings"

# ============================
# 5. STOCK ADJUSTMENTS
# ============================
class StockAdjustment(models.Model):
    ADJUSTMENT_REASONS = [
        ('spoilage', 'Spoilage / Expired'),
        ('damage', 'Damaged in Handling'),
        ('theft', 'Theft / Lost'),
        ('internal', 'Internal Use'),
        ('correction', 'Inventory Correction'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=20, choices=ADJUSTMENT_REASONS, default='spoilage')
    date = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} ({self.get_reason_display()})"
