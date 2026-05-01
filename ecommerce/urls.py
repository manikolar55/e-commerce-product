"""
Main URL configuration for BabyLady eCommerce
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from store.sitemaps import (
    StaticViewSitemap, ProductSitemap, CategorySitemap, BlogSitemap
)

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'blog': BlogSitemap,
}

urlpatterns = [
    # Django admin (hidden URL for security)
    path('super-admin-panel/', admin.site.urls),

    # Main store
    path('', include('store.urls', namespace='store')),

    # Orders
    path('orders/', include('orders.urls', namespace='orders')),

    # Accounts
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Admin dashboard
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),

    # Blog
    path('blog/', include('blog.urls', namespace='blog')),

    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Serve media/static in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'store.views.error_404'
handler500 = 'store.views.error_500'
