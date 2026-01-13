from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # We removed 'sku' and added 'cost_price'
    list_display = ('name', 'category', 'stock_quantity', 'price', 'cost_price', 'low_stock_threshold')
    list_filter = ('category',)
    search_fields = ('name',)
