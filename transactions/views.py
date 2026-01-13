from django.shortcuts import render, redirect
from .models import SalesOrder, SalesItem
from inventory.models import Product
from partners.models import Customer  # <--- IMPORTED CUSTOMER MODEL
from django.contrib import messages
from django.db import transaction

def new_sale(request):
    products = Product.objects.all()

    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        product_ids = request.POST.getlist("product_ids")
        quantities = request.POST.getlist("quantities")

        total_amount = 0

        try:
            with transaction.atomic():
                # 1. HANDLE CUSTOMER (The Fix)
                # This looks for a customer with that name. If not found, it creates one.
                customer, created = Customer.objects.get_or_create(name=customer_name)

                # 2. Create the Order linked to that REAL customer
                order = SalesOrder.objects.create(
                    customer=customer,
                    total_amount=0,
                    status="COMPLETED"
                )

                # 3. Add Items to the Order
                for p_id, qty in zip(product_ids, quantities):
                    qty = int(qty)
                    if qty > 0:
                        product = Product.objects.get(id=p_id)

                        # Check Stock
                        if product.stock_quantity < qty:
                            raise ValueError(f"Not enough stock for {product.name}")

                        # Deduct Stock
                        product.stock_quantity -= qty
                        product.save()

                        # Calculate Item Total
                        item_total = product.price * qty
                        total_amount += item_total

                        # Create SalesItem
                        # We don't need to pass total_price here because your
                        # SalesItem model calculates it automatically in its save() method.
                        SalesItem.objects.create(
                            order=order,
                            product=product,
                            quantity=qty,
                            unit_price=product.price
                        )

                # 4. Update Order Total
                order.total_amount = total_amount
                order.save()

                messages.success(request, f"Sale recorded for {customer.name}!")
                return redirect('dashboard')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, 'transactions/new_sale.html', {'products': products})

def order_list(request):
    # Show newest orders first
    orders = SalesOrder.objects.select_related('customer').all().order_by('-date')
    return render(request, 'transactions/order_list.html', {'orders': orders})
