from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Count, Q
from django.db import transaction
from django.db.models.functions import TruncDate
from django.utils import timezone
import json
from datetime import timedelta, date

# --- PAGINATION IMPORT ---
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# --- AUTH IMPORTS ---
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Models
from .models import Product, Category, Supplier, PurchaseOrder, SystemSettings
from sales.models import Order, OrderItem, Customer
# Forms
from .forms import ProductForm, CategoryForm, SupplierForm, PurchaseOrderForm, CustomerForm

# ==========================
# 0. AUTHENTICATION
# ==========================
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account was created.")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# ==========================
# 1. DASHBOARD (UPDATED: CASH BASIS)
# ==========================
@login_required
def dashboard(request):
    # Defaults
    total_revenue = 0
    total_orders = 0
    total_products = Product.objects.count()
    gross_profit = 0

    # --- Time Range Filter ---
    range_param = request.GET.get('range', '30')
    try:
        days_range = int(range_param)
        if days_range not in [30, 60, 90]:
            days_range = 30
    except ValueError:
        days_range = 30

    chart_dates = []
    chart_revenue = []
    top_product_names = []
    top_product_qtys = []
    stock_names = []
    stock_levels = []

    if Order.objects.exists():
        # 1. TOTAL REVENUE (Only PAID orders)
        total_revenue = Order.objects.filter(payment_status='PAID').aggregate(sum=Sum('total_amount'))['sum'] or 0

        # 2. TOTAL ORDERS (We still count all orders to show activity volume)
        total_orders = Order.objects.count()

        # 3. GROSS PROFIT (Only on PAID orders)
        # We must filter COGS to paid orders to match the revenue logic
        cogs = OrderItem.objects.filter(order__payment_status='PAID').annotate(
            cost=ExpressionWrapper(F('quantity') * F('product__cost_price'), output_field=DecimalField())
        ).aggregate(sum=Sum('cost'))['sum'] or 0

        gross_profit = total_revenue - cogs

        # 4. SALES CHART (Only PAID orders)
        start_date = timezone.now() - timedelta(days=days_range)
        daily_sales = Order.objects.filter(date__gte=start_date, payment_status='PAID')\
            .annotate(date_only=TruncDate('date'))\
            .values('date_only')\
            .annotate(total=Sum('total_amount'))\
            .order_by('date_only')

        for entry in daily_sales:
            if entry['date_only']:
                chart_dates.append(entry['date_only'].strftime('%b %d'))
                chart_revenue.append(float(entry['total']))

        # Top Products (Based on confirmed sales only)
        top_products = OrderItem.objects.filter(order__payment_status='PAID').values('product__name')\
            .annotate(qty=Sum('quantity'))\
            .order_by('-qty')[:5]

        for item in top_products:
            top_product_names.append(item['product__name'])
            top_product_qtys.append(item['qty'])

    recent_orders = Order.objects.select_related('customer').order_by('-date')[:5]
    low_stock_items = Product.objects.filter(stock_quantity__lte=F('low_stock_threshold'))

    all_products = Product.objects.all().order_by('stock_quantity')[:20]
    for product in all_products:
        stock_names.append(product.name)
        stock_levels.append(product.stock_quantity)

    # Top Customers (Ranked by how much they actually PAID)
    top_customers = Customer.objects.annotate(
        total_spent=Sum('order__total_amount', filter=Q(order__payment_status='PAID')),
        order_count=Count('order')
    ).filter(total_spent__isnull=False).order_by('-total_spent')[:5]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'gross_profit': gross_profit,
        'recent_orders': recent_orders,
        'low_stock_items': low_stock_items,
        'top_customers': top_customers,
        'chart_dates': json.dumps(chart_dates),
        'chart_revenue': json.dumps(chart_revenue),
        'top_product_names': json.dumps(top_product_names),
        'top_product_qtys': json.dumps(top_product_qtys),
        'stock_names': json.dumps(stock_names),
        'stock_levels': json.dumps(stock_levels),
        'current_range': days_range
    }
    return render(request, 'inventory/dashboard.html', context)

# ==========================
# 2. FORECASTING
# ==========================
@login_required
def forecast_dashboard(request):
    products = Product.objects.all()
    selected_product_id = request.GET.get('product_id')
    if selected_product_id:
        selected_product = get_object_or_404(Product, id=selected_product_id)
    else:
        selected_product = products.first()

    if not selected_product:
        return render(request, 'inventory/forecast.html', {'products': []})

    days_back = 90
    start_date = timezone.now().date() - timedelta(days=days_back)

    # Forecasting usually looks at DEMAND (orders placed), not just paid ones.
    # So we keep this looking at all orders to predict stock needs accurately.
    sales_data = OrderItem.objects.filter(
        product=selected_product,
        order__date__gte=start_date
    ).annotate(
        day=TruncDate('order__date')
    ).values('day').annotate(
        total_qty=Sum('quantity')
    ).order_by('day')

    dates = []
    actual_sales = []
    sales_dict = {item['day']: item['total_qty'] for item in sales_data}
    current_date = start_date
    today = timezone.now().date()

    while current_date <= today:
        dates.append(current_date.strftime('%Y-%m-%d'))
        qty = sales_dict.get(current_date, 0)
        actual_sales.append(qty)
        current_date += timedelta(days=1)

    predicted_dates = []
    predicted_sales = []

    if len(actual_sales) >= 7:
        last_7_days_avg = sum(actual_sales[-7:]) / 7
    else:
        last_7_days_avg = sum(actual_sales) / len(actual_sales) if actual_sales else 0

    next_date = today + timedelta(days=1)
    for i in range(7):
        predicted_dates.append(next_date.strftime('%Y-%m-%d'))
        predicted_sales.append(round(last_7_days_avg, 2))
        next_date += timedelta(days=1)

    context = {
        'products': products,
        'selected_product': selected_product,
        'dates': json.dumps(dates),
        'actual_sales': json.dumps(actual_sales),
        'predicted_dates': json.dumps(predicted_dates),
        'predicted_sales': json.dumps(predicted_sales),
        'next_week_forecast': round(last_7_days_avg * 7, 2)
    }
    return render(request, 'inventory/forecast.html', context)

# ==========================
# 3. ORDER / SALES VIEWS
# ==========================

@login_required
def order_list(request):
    orders_list = Order.objects.select_related('customer').all()

    search_query = request.GET.get('q')
    if search_query:
        if search_query.isdigit():
            orders_list = orders_list.filter(Q(id=search_query) | Q(customer__name__icontains=search_query))
        else:
            orders_list = orders_list.filter(customer__name__icontains=search_query)

    sort_by = request.GET.get('sort', 'date')
    direction = request.GET.get('dir', 'desc')

    ordering_map = {
        'id': 'id',
        'date': 'date',
        'customer': 'customer__name',
        'amount': 'total_amount',
        'payment': 'payment_status',
        'delivery': 'delivery_status'
    }

    db_field = ordering_map.get(sort_by, 'date')
    if direction == 'desc':
        db_field = '-' + db_field

    orders_list = orders_list.order_by(db_field)

    page = request.GET.get('page', 1)
    paginator = Paginator(orders_list, 20)

    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    context = {
        'orders': orders,
        'current_sort': sort_by,
        'current_dir': direction,
        'next_dir': 'desc' if direction == 'asc' else 'asc',
        'search_query': search_query if search_query else ''
    }
    return render(request, 'inventory/my_orders_final.html', context)

@login_required
@transaction.atomic
def create_order(request):
    customers = Customer.objects.all()
    products = Product.objects.all()

    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        payment_status = request.POST.get('payment_status')
        delivery_status = request.POST.get('delivery_status')

        product_ids = request.POST.getlist('products')
        quantities = request.POST.getlist('quantities')

        if customer_id and product_ids and quantities:
            customer = get_object_or_404(Customer, id=customer_id)

            order = Order.objects.create(
                customer=customer,
                payment_status=payment_status,
                delivery_status=delivery_status,
                total_amount=0
            )

            total_order_amount = 0

            for p_id, qty in zip(product_ids, quantities):
                qty = int(qty)
                if qty > 0:
                    product = get_object_or_404(Product, id=p_id)

                    if product.stock_quantity >= qty:
                        line_total = product.price * qty
                        total_order_amount += line_total

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=qty,
                            price=product.price
                        )

                        product.stock_quantity -= qty
                        product.save()
                    else:
                        messages.error(request, f"Error: Not enough stock for {product.name} (Only {product.stock_quantity} left).")
                        transaction.set_rollback(True)
                        return render(request, 'inventory/create_order.html', {'customers': customers, 'products': products})

            order.total_amount = total_order_amount
            order.save()

            messages.success(request, f"Order #{order.id} created with {len(product_ids)} items!")
            return redirect('order_list')
        else:
            messages.error(request, "Please add at least one item.")

    return render(request, 'inventory/create_order.html', {
        'customers': customers,
        'products': products
    })

@login_required
def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        order.payment_status = request.POST.get('payment_status')
        order.delivery_status = request.POST.get('delivery_status')
        order.save()
        messages.success(request, f"Order #{order.id} statuses updated!")
        return redirect('order_list')

    return render(request, 'inventory/edit_order.html', {'order': order})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()
    return render(request, 'inventory/order_detail.html', {'order': order, 'items': items})

# ==========================
# 4. PRODUCT VIEWS
# ==========================
@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added!")
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/add_product.html', {'form': form, 'title': 'Add Product'})

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated!")
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/add_product.html', {'form': form, 'title': 'Edit Product'})

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product deleted!")
    return redirect('product_list')

@login_required
def add_stock(request):
    products = Product.objects.all()
    if request.method == "POST":
        product_id = request.POST.get('product')
        quantity = request.POST.get('quantity')
        if product_id and quantity:
            product = get_object_or_404(Product, id=product_id)
            product.stock_quantity += int(quantity)
            product.save()
            messages.success(request, f"Added {quantity} items to {product.name}")
            return redirect('product_list')
    return render(request, 'inventory/add_stock.html', {'products': products})

# ==========================
# 5. CATEGORY VIEWS
# ==========================
@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    form = CategoryForm()
    return render(request, 'inventory/category_list.html', {'categories': categories, 'form': form})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully!")
        else:
            messages.error(request, "Error: Category likely exists.")
    return redirect('category_list')

@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated!")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/add_category.html', {'form': form, 'title': 'Edit Category'})

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted!")
    return redirect('category_list')

# ==========================
# 6. SUPPLIER & PURCHASE
# ==========================
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@login_required
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New Supplier added!")
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'inventory/add_supplier.html', {'form': form})

@login_required
def create_purchase_order(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            po = form.save()
            product = po.product
            product.stock_quantity += po.quantity
            product.cost_price = po.unit_cost
            product.save()
            messages.success(request, f"Stock updated: {product.name} +{po.quantity}")
            return redirect('product_list')
    else:
        form = PurchaseOrderForm()
    return render(request, 'inventory/buy_stock.html', {'form': form})

@login_required
def purchase_history(request):
    purchases = PurchaseOrder.objects.select_related('supplier', 'product').order_by('-id')
    return render(request, 'inventory/purchase_history.html', {'purchases': purchases})

@login_required
def edit_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier details updated!")
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'inventory/add_supplier.html', {'form': form, 'title': 'Edit Supplier'})

@login_required
def purchase_invoice(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'inventory/purchase_invoice.html', {'po': po})

@login_required
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    messages.success(request, "Supplier deleted successfully!")
    return redirect('supplier_list')

# ==========================
# 7. CUSTOMER VIEWS
# ==========================
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'inventory/customer_list.html', {'customers': customers})

@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New Customer Added!")
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'inventory/add_customer.html', {'form': form, 'title': 'Add Customer'})

# ==========================
# 8. SETTINGS VIEW
# ==========================
@login_required
def settings_view(request):
    settings_obj, created = SystemSettings.objects.get_or_create(id=1)

    if request.method == 'POST':
        currency = request.POST.get('currency_symbol')
        if currency:
            settings_obj.currency_symbol = currency
            settings_obj.save()
            messages.success(request, f"Currency changed to {currency}")
            return redirect('settings')

    return render(request, 'inventory/settings.html', {'settings': settings_obj})
