from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'unit_price', 'total_price']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'note', 'changed_by', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'full_name', 'phone', 'city', 'total', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'city', 'province', 'created_at']
    search_fields = ['order_id', 'full_name', 'phone', 'city']
    readonly_fields = ['order_id', 'subtotal', 'total', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
