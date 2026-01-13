import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDate
from django.shortcuts import render
from inventory.models import Product
from transactions.models import SalesItem, SalesOrder  # Ensure SalesItem is imported

def dashboard_home(request):
    # --- EXISTING STATS ---
    total_products = Product.objects.count()
    total_orders = SalesOrder.objects.count()

    # Calculate Total Revenue
    revenue_data = SalesOrder.objects.aggregate(Sum("total_amount"))
    total_revenue = revenue_data["total_amount__sum"] or 0

    # --- NEW: CALCULATE NET INCOME (PROFIT) ---
    # Formula: (Selling Price - Cost Price) * Quantity
    profit_data = SalesItem.objects.aggregate(
        total_profit=Sum((F('unit_price') - F('product__cost_price')) * F('quantity'))
    )
    total_profit = profit_data['total_profit'] or 0

    # Get recent orders
    recent_orders = SalesOrder.objects.select_related("customer").order_by("-date")[:5]

    # Low stock items
    low_stock_items = Product.objects.filter(stock_quantity__lte=F('low_stock_threshold'))

    # --- PREPARE DATA FOR CHARTS ---

    # 1. Daily Sales (Line Chart)
    daily_sales = (
        SalesOrder.objects.annotate(day=TruncDate("date"))
        .values("day")
        .annotate(total=Sum("total_amount"))
        .order_by("day")
    )

    chart_dates = [x["day"].strftime("%Y-%m-%d") for x in daily_sales]
    chart_revenue = [float(x["total"]) for x in daily_sales]

    # 2. Top Selling Products (Bar/Pie Chart)
    top_products = (
        SalesItem.objects.values("product__name")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:5]
    )

    top_product_names = [x["product__name"] for x in top_products]
    top_product_qtys = [x["total_qty"] for x in top_products]

    context = {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_profit": total_profit,  # <--- Passed to template
        "recent_orders": recent_orders,
        "low_stock_items": low_stock_items,
        "chart_dates": json.dumps(chart_dates, cls=DjangoJSONEncoder),
        "chart_revenue": json.dumps(chart_revenue, cls=DjangoJSONEncoder),
        "top_product_names": json.dumps(top_product_names, cls=DjangoJSONEncoder),
        "top_product_qtys": json.dumps(top_product_qtys, cls=DjangoJSONEncoder),
    }
    return render(request, "dashboard/home.html", context)
