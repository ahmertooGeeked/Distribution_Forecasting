import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
# Make sure these match your actual app name (e.g., inventory)
from inventory.models import Customer, Product, Order, OrderItem, Category

class Command(BaseCommand):
    help = 'Seeds the database with realistic wholesale data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Wiping old data...")
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Customer.objects.all().delete()

        # 1. Create Category
        veg_category = Category.objects.create(name="Vegetables")

        # 2. Create Products (Name + Price Range)
        product_config = {
            'Potatoes': (40, 70),
            'Onions': (80, 150),
            'Tomatoes': (100, 200),
            'Garlic': (300, 450),
            'Ginger': (400, 600),
            'Carrots': (50, 90),
            'Cabbage': (60, 100)
        }

        products_objs = []
        for name, r in product_config.items():
            p = Product.objects.create(
                name=name,
                category=veg_category,
                price=r[1], # Default listing price (max of range)
                stock_quantity=1000
            )
            # Store range on object for loop use
            p.temp_range = r
            products_objs.append(p)

        # 3. Create Customers (Your new list)
        customer_names = [
            "Metro Cash & Carry", "Al-Fatah Superstore", "Green Valley Hypermarket",
            "Save Mart", "Imtiaz Super Market", "Chase Up", "City Cash & Carry",
            "Punjab Wholesalers", "Bismillah General Store", "Diamond Super Store",
            "Urban Grocers", "Bestway Wholesale", "Rainbow Cash & Carry",
            "Family Mart", "Decent Traders"
        ]

        customers = []
        for name in customer_names:
            c = Customer.objects.create(name=name)
            customers.append(c)

        # 4. Generate Orders & Items
        self.stdout.write("Generating 1000 orders...")

        start_date = datetime(2025, 1, 1)

        for _ in range(1000):
            # A. Create the Order Wrapper
            random_days = random.randint(0, 365)
            # Use timezone aware datetime
            order_date = timezone.make_aware(start_date + timedelta(days=random_days))
            cust = random.choice(customers)

            # Create Order (Total price 0 for now, we sum it up later)
            order = Order.objects.create(
                customer=cust,
                date_created=order_date,
                total_price=0
            )

            # B. Create Order Item
            prod = random.choice(products_objs)
            qty = random.randint(10, 100) # Wholesale amounts

            # Randomize price slightly for this specific deal
            min_p, max_p = prod.temp_range
            deal_price = round(random.uniform(min_p, max_p), 2)

            item_total = deal_price * qty

            OrderItem.objects.create(
                order=order,
                product=prod,
                quantity=qty,
                price=deal_price
            )

            # C. Update Order Total
            order.total_price = item_total
            order.save()

        self.stdout.write(self.style.SUCCESS('Successfully seeded 1000 orders with OrderItems!'))
