"""
Store views: home, product list, product detail, search, wishlist
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.conf import settings
from django.views.decorators.http import require_POST
from .models import (
    Category, SubCategory, Product, ProductImage,
    Wishlist, Review, Newsletter, Banner, SiteSettings
)
from orders.views import get_or_create_cart
import json


def home_view(request):
    banners = Banner.objects.filter(is_active=True)[:5]
    baby_category = Category.objects.filter(category_type='baby', is_active=True).first()
    ladies_category = Category.objects.filter(category_type='ladies', is_active=True).first()
    featured_baby = Product.objects.filter(
        category__category_type='baby', is_active=True, is_featured=True
    ).select_related('category').prefetch_related('images')[:8]
    featured_ladies = Product.objects.filter(
        category__category_type='ladies', is_active=True, is_featured=True
    ).select_related('category').prefetch_related('images')[:8]
    new_arrivals = Product.objects.filter(
        is_active=True, is_new_arrival=True
    ).prefetch_related('images').order_by('-created_at')[:8]
    best_sellers = Product.objects.filter(
        is_active=True, is_best_seller=True
    ).prefetch_related('images').order_by('-total_sold')[:8]
    categories = Category.objects.filter(is_active=True).prefetch_related('subcategories')

    return render(request, 'store/home.html', {
        'banners': banners,
        'baby_category': baby_category,
        'ladies_category': ladies_category,
        'featured_baby': featured_baby,
        'featured_ladies': featured_ladies,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'categories': categories,
    })


def product_list_view(request):
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    categories = Category.objects.filter(is_active=True)

    # Filter by category
    cat_slug = request.GET.get('category')
    subcat_slug = request.GET.get('subcategory')
    category = None
    subcategory = None

    if cat_slug:
        category = get_object_or_404(Category, slug=cat_slug)
        products = products.filter(category=category)
    if subcat_slug:
        subcategory = get_object_or_404(SubCategory, slug=subcat_slug)
        products = products.filter(subcategory=subcategory)

    # Filters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    size_filter = request.GET.get('size')
    color_filter = request.GET.get('color')
    sort = request.GET.get('sort', '-created_at')

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if size_filter:
        products = products.filter(sizes__name__icontains=size_filter)
    if color_filter:
        products = products.filter(colors__name__icontains=color_filter)

    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-created_at',
        'popular': '-total_sold',
        'name': 'name',
    }
    products = products.order_by(sort_options.get(sort, '-created_at'))

    paginator = Paginator(products, settings.PRODUCTS_PER_PAGE)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    return render(request, 'store/product_list.html', {
        'products': products_page,
        'categories': categories,
        'current_category': category,
        'current_subcategory': subcategory,
        'sort': sort,
    })


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        category=category, is_active=True
    ).prefetch_related('images')

    sort = request.GET.get('sort', '-created_at')
    sort_options = {
        'price_asc': 'price', 'price_desc': '-price',
        'newest': '-created_at', 'popular': '-total_sold',
    }
    products = products.order_by(sort_options.get(sort, '-created_at'))

    paginator = Paginator(products, settings.PRODUCTS_PER_PAGE)
    products_page = paginator.get_page(request.GET.get('page'))

    return render(request, 'store/category.html', {
        'category': category,
        'products': products_page,
        'sort': sort,
    })


def subcategory_view(request, cat_slug, slug):
    category = get_object_or_404(Category, slug=cat_slug)
    subcategory = get_object_or_404(SubCategory, slug=slug, category=category)
    products = Product.objects.filter(
        subcategory=subcategory, is_active=True
    ).prefetch_related('images')

    paginator = Paginator(products, settings.PRODUCTS_PER_PAGE)
    products_page = paginator.get_page(request.GET.get('page'))

    return render(request, 'store/category.html', {
        'category': category,
        'subcategory': subcategory,
        'products': products_page,
    })


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    images = product.images.all()
    reviews = product.reviews.filter(is_approved=True).select_related('customer')
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id).prefetch_related('images')[:4]

    # Track recently viewed
    recently_viewed = request.session.get('recently_viewed', [])
    if product.id not in recently_viewed:
        recently_viewed.insert(0, product.id)
        request.session['recently_viewed'] = recently_viewed[:10]

    recently_viewed_products = []
    if recently_viewed:
        rv_ids = [pid for pid in recently_viewed if pid != product.id][:4]
        if rv_ids:
            recently_viewed_products = list(Product.objects.filter(
                id__in=rv_ids, is_active=True
            ).prefetch_related('images'))

    # Check wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(customer=request.user, product=product).exists()

    # Review form handling
    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        title = request.POST.get('title', '')
        body = request.POST.get('body', '')
        if rating and body:
            Review.objects.update_or_create(
                product=product, customer=request.user,
                defaults={'rating': rating, 'title': title, 'body': body}
            )
            messages.success(request, 'Your review has been submitted!')
            return redirect('store:product_detail', slug=slug)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'images': images,
        'reviews': reviews,
        'related_products': related_products,
        'recently_viewed': recently_viewed_products,
        'in_wishlist': in_wishlist,
        'schema': product.get_schema_markup(),
    })


def search_view(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(sku__icontains=query),
            is_active=True
        ).select_related('category').prefetch_related('images').distinct()

    paginator = Paginator(products, settings.PRODUCTS_PER_PAGE)
    products_page = paginator.get_page(request.GET.get('page'))

    return render(request, 'store/search.html', {
        'products': products_page,
        'query': query,
        'count': products.count() if query else 0,
    })


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(
        customer=request.user
    ).select_related('product').prefetch_related('product__images')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
@require_POST
def toggle_wishlist(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    product = get_object_or_404(Product, id=product_id)

    wishlist_item, created = Wishlist.objects.get_or_create(
        customer=request.user, product=product
    )
    if not created:
        wishlist_item.delete()
        return JsonResponse({'status': 'removed', 'message': f'{product.name} removed from wishlist'})

    return JsonResponse({'status': 'added', 'message': f'{product.name} added to wishlist!'})


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            obj, created = Newsletter.objects.get_or_create(email=email)
            if created:
                messages.success(request, 'Thank you for subscribing to our newsletter!')
            else:
                obj.is_active = True
                obj.save()
                messages.info(request, 'You are already subscribed!')
    return redirect(request.META.get('HTTP_REFERER', 'store:home'))


def robots_txt(request):
    content = f"""User-agent: *
Allow: /
Disallow: /dashboard/
Disallow: /super-admin-panel/
Disallow: /accounts/
Disallow: /orders/cart/
Disallow: /orders/checkout/

Sitemap: {settings.SITE_URL}/sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')


def error_404(request, exception):
    return render(request, 'store/404.html', status=404)


def error_500(request):
    return render(request, 'store/500.html', status=500)
