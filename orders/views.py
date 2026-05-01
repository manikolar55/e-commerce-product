"""
Order views: checkout, confirmation, tracking
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from store.models import Cart, CartItem, Coupon, Product
from .models import Order, OrderItem, OrderStatusHistory
from .forms import CheckoutForm
import json


def get_or_create_cart(request):
    """Get cart from session or user"""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(customer=request.user)
        # Merge session cart if exists
        session_key = request.session.get('cart_session_key')
        if session_key:
            try:
                session_cart = Cart.objects.get(session_key=session_key, customer=None)
                for item in session_cart.items.all():
                    existing = cart.items.filter(
                        product=item.product, size=item.size, color=item.color
                    ).first()
                    if existing:
                        existing.quantity += item.quantity
                        existing.save()
                    else:
                        item.cart = cart
                        item.save()
                session_cart.delete()
                del request.session['cart_session_key']
            except Cart.DoesNotExist:
                pass
        return cart
    else:
        session_key = request.session.get('cart_session_key')
        if not session_key:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            request.session['cart_session_key'] = session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, customer=None)
        return cart


def cart_view(request):
    cart = get_or_create_cart(request)
    coupon_code = request.session.get('coupon_code')
    coupon = None
    discount = 0

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            valid, msg = coupon.is_valid(cart.subtotal)
            if valid:
                discount = coupon.calculate_discount(cart.subtotal)
            else:
                del request.session['coupon_code']
                messages.warning(request, msg)
                coupon = None
        except Coupon.DoesNotExist:
            del request.session['coupon_code']

    total_after_discount = cart.subtotal - discount + cart.shipping_cost

    return render(request, 'store/cart.html', {
        'cart': cart,
        'coupon': coupon,
        'discount': discount,
        'total_after_discount': total_after_discount,
    })


@require_POST
def add_to_cart(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    size_id = data.get('size_id')
    color_id = data.get('color_id')

    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request)

    from store.models import Size, Color
    size = Size.objects.filter(id=size_id).first() if size_id else None
    color = Color.objects.filter(id=color_id).first() if color_id else None

    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, size=size, color=color,
        defaults={'quantity': quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()

    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to cart!',
        'cart_count': cart.total_items,
    })


@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()
    messages.success(request, 'Cart updated.')
    return redirect('orders:cart')


@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('orders:cart')


@require_POST
def apply_coupon(request):
    code = request.POST.get('coupon_code', '').strip().upper()
    cart = get_or_create_cart(request)

    try:
        coupon = Coupon.objects.get(code=code)
        valid, msg = coupon.is_valid(cart.subtotal)
        if valid:
            request.session['coupon_code'] = code
            discount = coupon.calculate_discount(cart.subtotal)
            messages.success(request, f'Coupon applied! You save Rs.{discount:.0f}')
        else:
            messages.error(request, msg)
    except Coupon.DoesNotExist:
        messages.error(request, 'Invalid coupon code.')

    return redirect('orders:cart')


@require_POST
def remove_coupon(request):
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    messages.info(request, 'Coupon removed.')
    return redirect('orders:cart')


def checkout_view(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('orders:cart')

    coupon_code = request.session.get('coupon_code')
    coupon = None
    discount = 0

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            valid, _ = coupon.is_valid(cart.subtotal)
            if valid:
                discount = coupon.calculate_discount(cart.subtotal)
        except Coupon.DoesNotExist:
            pass

    # Pre-fill if logged in
    initial = {}
    if request.user.is_authenticated:
        u = request.user
        initial = {'full_name': u.get_full_name(), 'phone': u.phone, 'email': u.email}
        default_addr = u.addresses.filter(is_default=True).first()
        if default_addr:
            initial.update({
                'address': default_addr.address_line,
                'city': default_addr.city,
                'province': default_addr.province,
                'postal_code': default_addr.postal_code,
            })

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.subtotal = cart.subtotal
            order.shipping_cost = cart.shipping_cost
            order.discount_amount = discount
            order.total = cart.subtotal + cart.shipping_cost - discount
            if coupon:
                order.coupon = coupon
                coupon.used_count += 1
                coupon.save()
            if request.user.is_authenticated:
                order.customer = request.user
            order.save()

            # Create order items
            for cart_item in cart.items.all():
                img = cart_item.product.main_image
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_sku=cart_item.product.sku,
                    size=cart_item.size,
                    color=cart_item.color,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.selling_price,
                    product_image=img.image.url if img else '',
                )
                cart_item.product.total_sold += cart_item.quantity
                cart_item.product.stock = max(0, cart_item.product.stock - cart_item.quantity)
                cart_item.product.save()

            OrderStatusHistory.objects.create(order=order, new_status='pending')

            if request.user.is_authenticated:
                request.user.total_orders += 1
                request.user.total_spent += order.total
                request.user.save()

            cart.items.all().delete()
            if 'coupon_code' in request.session:
                del request.session['coupon_code']

            return redirect('orders:confirmation', order_id=order.order_id)
    else:
        form = CheckoutForm(initial=initial)

    total = cart.subtotal + cart.shipping_cost - discount

    return render(request, 'store/checkout.html', {
        'form': form,
        'cart': cart,
        'coupon': coupon,
        'discount': discount,
        'total': total,
    })


def order_confirmation_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'store/order_confirmation.html', {'order': order})


def order_tracking_view(request):
    order = None
    if request.method == 'POST':
        order_id = request.POST.get('order_id', '').strip().upper()
        phone = request.POST.get('phone', '').strip()
        try:
            order = Order.objects.get(order_id=order_id, phone=phone)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found. Check your Order ID and phone number.')

    return render(request, 'store/order_tracking.html', {'order': order})
