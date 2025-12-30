# restaurant/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ===== TABLE MANAGEMENT =====
    path('tables/', views.get_all_tables, name='get_all_tables'),
    path('tables/create/', views.create_table, name='create_table'),
    path('tables/update/<int:table_id>/', views.update_table, name='update_table'),
    path('tables/delete/<int:table_id>/', views.delete_table, name='delete_table'),
    
    # ===== MENU MANAGEMENT =====
    path('menu/', views.get_menu_items, name='get_menu_items'),
    path('menu/create/', views.create_menu_item, name='create_menu_item'),
    path('menu/update/<int:item_id>/', views.update_menu_item, name='update_menu_item'),
    path('menu/delete/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),
    
    # ===== ORDER MANAGEMENT =====
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('orders/table/<int:table_id>/', views.get_table_orders, name='get_table_orders'),
    
    # ===== BILLING =====
    path('bills/generate/', views.generate_bill, name='generate_bill'),
    path('bills/mark-paid/<int:bill_id>/', views.mark_bill_paid, name='mark_bill_paid'),
    path('bills/pending/', views.get_pending_bills, name='get_pending_bills'),
    path('tables/ready-for-bill/', views.get_tables_ready_for_bill, name='get_tables_ready_for_bill'),
    path('bills/<int:bill_id>/', views.get_bill_details, name='get_bill_details'),
    path('cashier/stats/', views.get_cashier_stats, name='get_cashier_stats'),

    path('bills/overdue/', views.get_overdue_bills, name='get_overdue_bills'),
]