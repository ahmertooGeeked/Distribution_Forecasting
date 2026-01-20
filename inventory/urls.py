from django.urls import path
from . import views

urlpatterns = [
    # --- Dashboard ---
    path('', views.dashboard, name='dashboard'),

    # --- Forecaster ---
    path('forecast/', views.forecast_dashboard, name='forecast_dashboard'),

    # --- Products ---
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),

    # --- Categories ---
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # --- Stock & Suppliers ---
    path('stock/add/', views.add_stock, name='add_stock'),
    path('stock/waste/', views.report_waste, name='report_waste'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/edit/<int:pk>/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/delete/<int:pk>/', views.delete_supplier, name='delete_supplier'),

    # --- Purchasing ---
    path('purchase/new/', views.create_purchase_order, name='create_purchase_order'),
    path('purchase/history/', views.purchase_history, name='purchase_history'),
    path('purchase/invoice/<int:pk>/', views.purchase_invoice, name='purchase_invoice'),

    # --- SALES & ORDERS ---
    path('orders/', views.order_list, name='order_list'),
    path('orders/new/', views.create_order, name='create_order'),
    path('orders/edit/<int:pk>/', views.edit_order, name='edit_order'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),

    # --- CUSTOMERS ---
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    # --- NEW: Added Edit Customer Path ---
    path('customers/edit/<int:pk>/', views.edit_customer, name='edit_customer'),

    # --- FINANCE ---
    path('finance/receivables/', views.receivables_dashboard, name='receivables_dashboard'),
    path('finance/report/', views.financial_report, name='financial_report'),

    # --- LOGISTICS ---
    path('logistics/', views.delivery_dashboard, name='delivery_dashboard'),
    path('logistics/run-sheet/', views.generate_run_sheet, name='generate_run_sheet'),

    # --- Authentication ---
    path('register/', views.register, name='register'),

    path('settings/', views.settings_view, name='settings'),
]
