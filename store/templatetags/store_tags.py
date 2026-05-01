"""Custom template tags for the store"""
from django import template
from store.models import Product, Category

register = template.Library()


@register.simple_tag
def get_featured_products(count=4):
    return Product.objects.filter(is_active=True, is_featured=True)[:count]


@register.simple_tag
def get_categories():
    return Category.objects.filter(is_active=True)


@register.filter
def multiply(value, arg):
    return value * arg


@register.filter
def subtract(value, arg):
    return value - arg


@register.inclusion_tag('store/includes/product_card.html')
def product_card(product):
    return {'product': product}
