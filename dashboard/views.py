"""
Admin dashboard views: overview, products, orders, customers, reports
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings
from datetime import timedelta, date
import csv
import io
from store.models import (
    Category, SubCategory, Product, ProductImage,
    Size, Color, Coupon, Review, Newsletter, Banner, SiteSettings
)
from orders.models import Order, OrderItem, OrderStatusHistory
from accounts.models import Customer
from .forms import (
    ProductForm, ProductImageFormSet, CategoryForm,
    CouponForm, BannerForm, SiteSettingsForm
)


def is_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


staff_required = user_passes_test(is_staff, login_url='/accounts/login/')


@login_required
@staff_required
def dashboard_home(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Order stats
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    confirmed_orders = Order.objects.filter(status='confirmed').count()
    shipped_orders = Order.objects.filter(status='shipped').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    paid_orders = Order.objects.filter(payment_status='paid').count()

    # Revenue
    revenue_today = Order.objects.filter(
        created_at__date=today,
        status__in=['confirmed', 'shipped', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0

    revenue_month = Order.objects.filter(
        created_at__date__gte=month_start,
        status__in=['confirmed', 'shipped', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0

    # Top products
    top_products = Product.objects.filter(
        is_active=True
    ).order_by('-total_sold')[:5]

    # Recent orders
    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:10]

    # Revenue chart data (last 30 days)
    chart_data = []
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        rev = Order.objects.filter(
            created_at__date=d,
            status__in=['confirmed', 'shipped', 'delivered']
        ).aggregate(total=Sum('total'))['total'] or 0
        chart_data.append({'date': d.strftime('%b %d'), 'revenue': float(rev)})

    # Customer count
    total_customers = Customer.objects.filter(is_staff=False).count()
    new_customers_today = Customer.objects.filter(date_joined__date=today, is_staff=False).count()

    return render(request, 'dashboard/home.html', {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'paid_orders': paid_orders,
        'revenue_today': revenue_today,
        'revenue_month': revenue_month,
        'top_products': top_products,
        'recent_orders': recent_orders,
        'chart_data': chart_data,
        'total_customers': total_customers,
        'new_customers_today': new_customers_today,
        'total_products': Product.objects.filter(is_active=True).count(),
        'low_stock': Product.objects.filter(is_active=True, stock__lt=10).count(),
    })


# ===== PRODUCT MANAGEMENT =====

@login_required
@staff_required
def product_list(request):
    products = Product.objects.select_related('category').prefetch_related('images').order_by('-created_at')
    search = request.GET.get('search', '')
    cat_filter = request.GET.get('category', '')
    if search:
        products = products.filter(Q(name__icontains=search) | Q(sku__icontains=search))
    if cat_filter:
        products = products.filter(category__id=cat_filter)

    paginator = Paginator(products, 20)
    products_page = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()

    return render(request, 'dashboard/products/list.html', {
        'products': products_page,
        'categories': categories,
        'search': search,
        'cat_filter': cat_filter,
    })


@login_required
@staff_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            # Handle multiple images
            images = request.FILES.getlist('images')
            for i, img in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=img,
                    is_primary=(i == 0),
                    order=i,
                    alt_text=product.name
                )
            messages.success(request, f'Product "{product.name}" added successfully.')
            return redirect('dashboard:product_edit', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'dashboard/products/form.html', {'form': form, 'title': 'Add Product'})


@login_required
@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            # Handle new images
            images = request.FILES.getlist('images')
            existing_count = product.images.count()
            for i, img in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=img,
                    is_primary=(existing_count == 0 and i == 0),
                    order=existing_count + i,
                    alt_text=product.name
                )
            messages.success(request, 'Product updated successfully.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/products/form.html', {
        'form': form, 'product': product, 'title': 'Edit Product'
    })


@login_required
@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.is_active = False
        product.save()
        messages.success(request, f'Product "{product.name}" deactivated.')
    return redirect('dashboard:product_list')


@login_required
@staff_required
def product_image_delete(request, pk):
    img = get_object_or_404(ProductImage, pk=pk)
    img.delete()
    return JsonResponse({'success': True})


# ===== ORDER MANAGEMENT =====

@login_required
@staff_required
def order_list(request):
    orders = Order.objects.select_related('customer').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    payment_filter = request.GET.get('payment', '')
    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if status_filter:
        orders = orders.filter(status=status_filter)
    if payment_filter:
        orders = orders.filter(payment_status=payment_filter)
    if search:
        orders = orders.filter(
            Q(order_id__icontains=search) |
            Q(full_name__icontains=search) |
            Q(phone__icontains=search)
        )
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)

    paginator = Paginator(orders, settings.ORDERS_PER_PAGE)
    orders_page = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/orders/list.html', {
        'orders': orders_page,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'search': search,
        'status_choices': Order.STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_STATUS_CHOICES,
    })


@login_required
@staff_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    history = order.history.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_status':
            old_status = order.status
            new_status = request.POST.get('status')
            note = request.POST.get('note', '')
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                if new_status == 'confirmed':
                    order.confirmed_at = timezone.now()
                elif new_status == 'shipped':
                    order.shipped_at = timezone.now()
                    order.tracking_number = request.POST.get('tracking_number', '')
                    order.courier = request.POST.get('courier', '')
                elif new_status == 'delivered':
                    order.delivered_at = timezone.now()
                order.save()
                OrderStatusHistory.objects.create(
                    order=order, old_status=old_status,
                    new_status=new_status, note=note,
                    changed_by=request.user
                )
                messages.success(request, f'Order status updated to {new_status}.')

        elif action == 'mark_paid':
            order.payment_status = 'paid'
            order.save()
            messages.success(request, 'Order marked as paid.')

        return redirect('dashboard:order_detail', order_id=order_id)

    return render(request, 'dashboard/orders/detail.html', {
        'order': order,
        'history': history,
        'status_choices': Order.STATUS_CHOICES,
    })


@login_required
@staff_required
def export_orders_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Order ID', 'Customer', 'Phone', 'City', 'Province',
        'Total', 'Status', 'Payment', 'Date'
    ])

    orders = Order.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    for order in orders:
        writer.writerow([
            order.order_id,
            order.full_name,
            order.phone,
            order.city,
            order.province,
            order.total,
            order.get_status_display(),
            order.get_payment_status_display(),
            order.created_at.strftime('%Y-%m-%d %H:%M'),
        ])

    return response


# ===== REPORTS =====

@login_required
@staff_required
def reports_view(request):
    today = timezone.now().date()
    report_type = request.GET.get('type', 'monthly')

    if report_type == 'daily':
        days = int(request.GET.get('days', 7))
        data = []
        for i in range(days - 1, -1, -1):
            d = today - timedelta(days=i)
            stats = Order.objects.filter(created_at__date=d).aggregate(
                total_orders=Count('id'),
                revenue=Sum('total'),
                delivered=Count('id', filter=Q(status='delivered')),
                pending=Count('id', filter=Q(status='pending')),
            )
            data.append({'date': d.strftime('%Y-%m-%d'), **{k: v or 0 for k, v in stats.items()}})

    elif report_type == 'monthly':
        months = int(request.GET.get('months', 6))
        data = []
        for i in range(months - 1, -1, -1):
            if today.month - i <= 0:
                year = today.year - 1
                month = today.month - i + 12
            else:
                year = today.year
                month = today.month - i
            stats = Order.objects.filter(
                created_at__year=year, created_at__month=month
            ).aggregate(
                total_orders=Count('id'),
                revenue=Sum('total'),
                delivered=Count('id', filter=Q(status='delivered')),
            )
            data.append({
                'date': f"{year}-{month:02d}",
                **{k: v or 0 for k, v in stats.items()}
            })

    # Best selling products
    best_products = Product.objects.filter(is_active=True).order_by('-total_sold')[:10]

    # Revenue summary
    total_revenue = Order.objects.filter(
        status__in=['confirmed', 'shipped', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0

    return render(request, 'dashboard/reports.html', {
        'data': data,
        'report_type': report_type,
        'best_products': best_products,
        'total_revenue': total_revenue,
    })


# ===== CUSTOMER MANAGEMENT =====

@login_required
@staff_required
def customer_list(request):
    customers = Customer.objects.filter(is_staff=False).order_by('-date_joined')
    search = request.GET.get('search', '')
    if search:
        customers = customers.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(phone__icontains=search)
        )
    paginator = Paginator(customers, 20)
    return render(request, 'dashboard/customers/list.html', {
        'customers': paginator.get_page(request.GET.get('page')),
        'search': search,
    })


@login_required
@staff_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'dashboard/customers/detail.html', {
        'customer': customer,
        'orders': orders,
    })


# ===== CATEGORIES =====

@login_required
@staff_required
def category_list(request):
    categories = Category.objects.prefetch_related('subcategories').all()
    return render(request, 'dashboard/categories/list.html', {'categories': categories})


@login_required
@staff_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/categories/form.html', {'form': form, 'title': 'Add Category'})


@login_required
@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/categories/form.html', {'form': form, 'title': 'Edit Category'})


# ===== COUPONS =====

@login_required
@staff_required
def coupon_list(request):
    coupons = Coupon.objects.all().order_by('-created_at')
    return render(request, 'dashboard/coupons/list.html', {'coupons': coupons})


@login_required
@staff_required
def coupon_add(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created.')
            return redirect('dashboard:coupon_list')
    else:
        form = CouponForm()
    return render(request, 'dashboard/coupons/form.html', {'form': form, 'title': 'Add Coupon'})


# ===== SITE SETTINGS =====

@login_required
@staff_required
def site_settings_view(request):
    obj = SiteSettings.get_settings()
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings saved.')
            return redirect('dashboard:settings')
    else:
        form = SiteSettingsForm(instance=obj)
    return render(request, 'dashboard/settings.html', {'form': form})
