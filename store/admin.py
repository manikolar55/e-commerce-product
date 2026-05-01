from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, SubCategory, Product, ProductImage,
    Size, Color, Coupon, Wishlist, Review, Newsletter,
    SiteSettings, Banner
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'product_count', 'is_active', 'order']
    list_filter = ['category_type', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'order']


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'order']
    list_filter = ['category', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_active', 'is_featured', 'total_sold']
    list_filter = ['category', 'is_active', 'is_featured', 'is_new_arrival', 'is_best_seller']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'discount_price', 'stock', 'is_active', 'is_featured']
    filter_horizontal = ['sizes', 'colors']
    inlines = [ProductImageInline]
    readonly_fields = ['sku', 'total_sold', 'created_at', 'updated_at']


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code', 'color_preview']

    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width:20px;height:20px;background:{};border-radius:50%;display:inline-block;"></div>',
                obj.hex_code
            )
        return '-'
    color_preview.short_description = 'Preview'


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'used_count', 'is_active', 'valid_until']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    list_editable = ['is_approved']


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order']
    list_editable = ['is_active', 'order']
