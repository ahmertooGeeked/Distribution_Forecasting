import os
import random
import django
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

# 1. Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangofirst.settings")
django.setup()

from inventory.models import Category, Product, Supplier
from sales.models import Customer, Order, OrderItem

def run():
    print("--- 🚀 STARTING SMART DATA GENERATION (FIXED DATES) ---")

    print("🧹 Flushing old data...")
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    Customer.objects.all().delete()
    Supplier.objects.all().delete()

    # 1. Categories
    print("📦 Creating Categories...")
    categories = ['Vegetables', 'Fruits', 'Bakery', 'Dairy', 'Beverages', 'Meat', 'Pantry', 'Household']
    cat_objs = {name: Category.objects.create(name=name) for name in categories}

    # 2. Suppliers
    print("🚚 Creating Suppliers...")
    suppliers = ['FarmFresh Distributors', 'Daily Dairy Co.', 'Global Beverages', 'City Bakery Supply', 'Home Essentials Ltd']
    for s in suppliers:
        Supplier.objects.create(name=s, email=f"contact@{s.replace(' ','').lower()}.com")

    # 3. Product Definitions
    raw_products = [
        ('Potatoes', 'Vegetables', 0.50),
        ('Onions', 'Vegetables', 0.40),
        ('Tomatoes', 'Vegetables', 0.80),
        ('Carrots', 'Vegetables', 0.60),
        ('Apples', 'Fruits', 1.20),
        ('Bananas', 'Fruits', 0.90),
        ('Oranges', 'Fruits', 1.50),
        ('White Bread', 'Bakery', 1.00),
        ('Whole Wheat Bread', 'Bakery', 1.50),
        ('Multigrain Bread', 'Bakery', 1.80),
        ('Whole Milk', 'Dairy', 1.20),
        ('Low Fat Milk', 'Dairy', 1.20),
        ('Mineral Water', 'Beverages', 0.30),
        ('Orange Juice', 'Beverages', 2.00),
        ('Cola', 'Beverages', 0.80),
        ('Chicken Breast', 'Meat', 4.50),
        ('Beef Mince', 'Meat', 5.50),
        ('Rice', 'Pantry', 1.50),
        ('Pasta', 'Pantry', 0.90),
        ('Dish Soap', 'Household', 2.00),
    ]

    print("🛒 Creating Products...")
    prod_objs = []

    for name, cat, base_cost in raw_products:
        variants = []
        if cat in ['Vegetables', 'Fruits', 'Meat']:
            variants.append((f"{name} (1kg)", base_cost * 2.0))
            variants.append((f"{name} (0.5kg)", base_cost * 1.1))
        elif cat == 'Bakery':
            variants.append((f"{name} (Full Loaf)", base_cost * 2.0))
            variants.append((f"{name} (Half Loaf)", base_cost * 1.1))
        elif cat in ['Dairy', 'Beverages']:
            variants.append((f"{name} (1L)", base_cost * 2.0))
            variants.append((f"{name} (0.5L)", base_cost * 1.1))
        else:
            variants.append((f"{name} (Standard Pack)", base_cost * 1.5))

        for p_name, p_cost in variants:
            p_price = p_cost * 1.3
            p = Product.objects.create(
                name=p_name,
                category=cat_objs[cat],
                cost_price=Decimal(f"{p_cost:.2f}"),
                price=Decimal(f"{p_price:.2f}"),
                stock_quantity=random.randint(20, 200)
            )
            prod_objs.append(p)

    # 4. Customers
    print("👥 Creating Customers...")
    customer_names = ['City Mart', 'Green Grocers', 'Healthy Bites Cafe', 'Corner Store', 'Family Mart', 'Fresh Stop']
    customers = [Customer.objects.create(name=n, email=f"{n.split()[0].lower()}@mail.com", phone="555-0100") for n in customer_names]

    # 5. Generate 2 Years of Sales
    print("⏳ Generating 2 Years of Orders...")

    end_date = timezone.now()

    with transaction.atomic():
        for i in range(800):
            # 1. Randomize Date
            days_ago = int(random.triangular(0, 730, 0)) # Weighted to recent
            order_date = end_date - timedelta(days=days_ago)

            # 2. Create Order (Initially today)
            order = Order.objects.create(
                customer=random.choice(customers),
                payment_status='PAID',
                delivery_status='DELIVERED' if days_ago > 2 else 'PENDING',
                total_amount=0
            )

            # 3. Add Items
            total = Decimal("0.00")
            for _ in range(random.randint(1, 8)):
                prod = random.choice(prod_objs)
                qty = random.randint(1, 5)

                line_total = prod.price * qty
                total += line_total

                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=qty,
                    price=prod.price
                )

            # 4. Save Total (This might reset date if auto_now=True)
            order.total_amount = total
            order.save()

            # 5. FORCE UPDATE DATE (This MUST be last)
            # This bypasses the 'save()' method and directly updates the DB column
            Order.objects.filter(id=order.id).update(date=order_date)

    print("--- 🎉 DATA GENERATION COMPLETE! ---")

if __name__ == "__main__":
    run()
