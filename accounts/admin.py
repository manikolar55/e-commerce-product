from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer, Address


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'phone', 'total_orders', 'total_spent', 'date_joined']
    list_filter = ['is_active', 'is_newsletter_subscribed', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Customer Info', {'fields': ('phone', 'avatar', 'date_of_birth', 'is_newsletter_subscribed', 'total_orders', 'total_spent')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'customer', 'city', 'province', 'is_default']
    list_filter = ['city', 'province', 'is_default']
    search_fields = ['full_name', 'customer__email', 'city']
