"""
Global context processors: cart count, categories, wishlist, site settings
"""
from .models import Category, Wishlist, SiteSettings


def cart_processor(request):
    """Add cart item count to all templates"""
    cart_count = 0
    try:
        from orders.views import get_or_create_cart
        cart = get_or_create_cart(request)
        cart_count = cart.total_items
    except Exception:
        pass
    return {'cart_count': cart_count}


def categories_processor(request):
    """Add all active categories to context"""
    baby_cats = Category.objects.filter(
        category_type='baby', is_active=True
    ).prefetch_related('subcategories')
    ladies_cats = Category.objects.filter(
        category_type='ladies', is_active=True
    ).prefetch_related('subcategories')
    return {
        'nav_baby_cats': baby_cats,
        'nav_ladies_cats': ladies_cats,
        'all_categories': list(baby_cats) + list(ladies_cats),
    }


def wishlist_processor(request):
    """Add wishlist count for authenticated users"""
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(customer=request.user).count()
    return {'wishlist_count': wishlist_count}


def site_settings_processor(request):
    """Add site settings to all templates"""
    settings = SiteSettings.get_settings()
    return {'site_settings': settings}
