from django.urls import path
from . import views

urlpatterns = [
    # Path for adding a new customer
    path('add-customer/', views.add_customer, name='add_customer'),

    # Path for creating a new sale/order
    path('create/', views.create_order, name='create_order'),

    # Path for viewing the list of past orders
    path('list/', views.order_list, name='order_list'),
]
