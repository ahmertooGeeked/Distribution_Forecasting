from django.contrib import admin
from django.urls import path, include  # <--- Added 'include' here
from inventory import views
from django.contrib.auth import views as auth_views
from django.conf import settings               # <--- Add this
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- DASHBOARD & FORECASTING ---
    path("", views.dashboard, name="dashboard"),
    path('forecast/', views.forecast_dashboard, name='forecast_dashboard'),

    # --- AUTH SYSTEM ---
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),

    # --- PRODUCTS ---
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.add_product, name="add_product"),
    path("products/edit/<int:pk>/", views.edit_product, name="edit_product"),
    path("products/delete/<int:pk>/", views.delete_product, name="delete_product"),
    path("stock/add/", views.add_stock, name="add_stock"),

    # --- CATEGORIES ---
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.add_category, name="add_category"),
    path("categories/edit/<int:pk>/", views.edit_category, name="edit_category"),
    path("categories/delete/<int:pk>/", views.delete_category, name="delete_category"),

    # --- SALES APP (New) ---
    # This connects the new 'sales/urls.py' you just created.
    # Access these at: /sales/create/, /sales/list/, /sales/add-customer/
    #path('sales/', include('sales.urls')),
    path('', include('inventory.urls')),

    # --- OLD ORDERS / SALES (Commented out to avoid conflict) ---
    # These are now handled by the 'sales' app above.
    # path("orders/", views.order_list, name="order_list"),
    # path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    # path("orders/new/", views.create_order, name="create_order"),
    # path("new-sale/", views.create_order, name="new_sale"),

    # --- SUPPLIERS & PURCHASING ---
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/add/", views.add_supplier, name="add_supplier"),
    path("suppliers/edit/<int:pk>/", views.edit_supplier, name="edit_supplier"),
    path("suppliers/delete/<int:pk>/", views.delete_supplier, name="delete_supplier"),
    path("buy-stock/", views.create_purchase_order, name="create_purchase_order"),

    path("purchase-history/", views.purchase_history, name="purchase_history"),
    path("purchase-invoice/<int:pk>/", views.purchase_invoice, name="purchase_invoice"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
