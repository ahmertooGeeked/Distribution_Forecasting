from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemFormSet, CustomerForm  # Imported CustomerForm
from inventory.models import Product

# --- NEW: Add Customer View ---
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer added successfully!')
            # Redirects to 'create_order' so you can immediately use the new customer
            return redirect('create_order')
    else:
        form = CustomerForm()

    return render(request, 'sales/add_customer.html', {'form': form})

# --- Existing Views ---
def order_list(request):
    orders = Order.objects.all().order_by('-date')
    return render(request, 'sales/order_list.html', {'orders': orders})

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            try:
                # 1. Save the Order (Parent)
                order = form.save()

                # 2. Save the Items (Children)
                items = formset.save(commit=False)
                for item in items:
                    item.order = order
                    # 3. Deduct Stock
                    product = item.product
                    if product.stock_quantity >= item.quantity:
                        product.stock_quantity -= item.quantity
                        product.save()
                        item.save()
                    else:
                        raise ValueError(f"Not enough stock for {product.name}")

                # 4. Calculate Total Order Amount
                order.total_amount = sum(item.subtotal for item in order.items.all())
                order.save()

                messages.success(request, "Order created successfully!")
                return redirect('order_list')

            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, 'sales/create_order.html', {
        'form': form,
        'formset': formset
    })
