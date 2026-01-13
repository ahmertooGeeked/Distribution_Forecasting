import os
import random
from datetime import date, timedelta
from decimal import Decimal  # <--- Added this to fix the math

import django
from django.utils import timezone

# Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangofirst.settings")
django.setup()

from inventory.models import Category, Product
from partners.models import Customer, Supplier
from transactions.models import SalesItem, SalesOrder


def run():
    print("--- 🚀 STARTING DATA GENERATION ---")

    # 1. Create Categories
    cats = ["Vegetables", "Fruits", "Dairy", "Meat", "Beverages"]
    cat_objs = []
    for c in cats:
        obj, created = Category.objects.get_or_create(name=c)
        cat_objs.append(obj)
    print(f"✅ Categories Checked/Created")

    # 2. Create Suppliers
    suppliers = ["Fresh Farms Ltd", "Global Foods", "Dairy King", "Meat Masters"]
    for s in suppliers:
        Supplier.objects.get_or_create(
            name=s, email=f"contact@{s.replace(' ', '').lower()}.com"
        )
    print(f"✅ Suppliers Checked/Created")

    # 3. Create Products
    products_list = [
        ("Tomato", 0, 1.50),
        ("Potato", 0, 0.80),
        ("Onion", 0, 1.20),
        ("Apple", 1, 2.50),
        ("Banana", 1, 1.10),
        ("Orange", 1, 3.00),
        ("Milk 1L", 2, 1.50),
        ("Cheese", 2, 5.00),
        ("Yogurt", 2, 2.00),
        ("Beef Steak", 3, 15.00),
        ("Chicken Breast", 3, 8.50),
        ("Cola", 4, 1.00),
        ("Water 500ml", 4, 0.50),
    ]

    prod_objs = []
    for name, cat_idx, price in products_list:
        sku = f"{name[:3].upper()}-{random.randint(100, 999)}"
        prod, created = Product.objects.get_or_create(
            name=name,
            defaults={
                "category": cat_objs[cat_idx],
                "sku": sku,
                "price": price,
                "stock_quantity": random.randint(50, 500),
                "low_stock_threshold": 20,
            },
        )
        prod_objs.append(prod)
    print(f"✅ Products Checked/Created")

    # 4. Create Customers
    customer_names = [
        "Burger King",
        "Hilton Hotel",
        "Pizza Hut",
        "Local Cafe",
        "John Doe",
    ]
    cust_objs = []
    for name in customer_names:
        cust, created = Customer.objects.get_or_create(
            name=name,
            defaults={
                "credit_limit": 5000.00,
                "email": f"manager@{name.replace(' ', '').lower()}.com",
            },
        )
        cust_objs.append(cust)
    print(f"✅ Customers Checked/Created")

    # 5. Generate Fake Sales (History)
    print("⏳ Generating Sales History...")

    # We create 50 orders
    for _ in range(50):
        days_ago = random.randint(0, 30)
        order_date = timezone.now() - timedelta(days=days_ago)
        customer = random.choice(cust_objs)

        # Create Order
        order = SalesOrder.objects.create(customer=customer, status="COMPLETED")
        order.date = order_date
        order.save()

        # Add items and calculate Total
        total_order_price = Decimal("0.00")  # <--- Start as Decimal

        for _ in range(random.randint(1, 5)):
            prod = random.choice(prod_objs)
            qty = random.randint(1, 20)

            # FORCE CONVERSION TO DECIMAL TO FIX THE ERROR
            # We convert the price to string first, then to Decimal to be safe
            price_decimal = Decimal(str(prod.price))

            SalesItem.objects.create(
                order=order,
                product=prod,
                quantity=qty,
                unit_price=price_decimal,
                total_price=price_decimal * qty,
            )
            total_order_price += price_decimal * qty

        order.total_amount = total_order_price
        order.save()

    print(f"✅ Generated 50 Historical Sales Orders")
    print("--- 🎉 FINISHED! Your database is ready. ---")


if __name__ == "__main__":
    run()
