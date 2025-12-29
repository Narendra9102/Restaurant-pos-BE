# restaurant/admin.py
from django.contrib import admin
from .models import Table, MenuItem, Order, OrderItem, Bill


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'seating_capacity', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['table_number']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'created_at']
    list_filter = ['category', 'is_available']
    search_fields = ['name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'status', 'created_by', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['table__table_number']
    inlines = [OrderItemInline]


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'total_amount', 'status', 'generated_at', 'paid_at']
    list_filter = ['status', 'generated_at']
    search_fields = ['table__table_number']
    readonly_fields = ['subtotal', 'tax_amount', 'total_amount']

    