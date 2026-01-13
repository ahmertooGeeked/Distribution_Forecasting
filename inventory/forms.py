from django import forms

# 1. Import Inventory Models (Local)
from .models import Product, Category, Supplier, PurchaseOrder

# 2. Import Sales Models (From the new Sales app)
from sales.models import Order, Customer

# ============================
# INVENTORY FORMS
# ============================

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'cost_price', 'stock_quantity', 'low_stock_threshold']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email']

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'product', 'quantity', 'unit_cost']

# ============================
# SALES FORMS
# ============================

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        # Note: I changed 'total_price' to 'total_amount' to match the new sales/models.py
        fields = ['customer', 'total_amount']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address']
