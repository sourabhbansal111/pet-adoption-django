from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Product,Order,OrderItem
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
import random
# Create your views here.

def _cart_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def add_to_cart(request, product_id):
    
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()
    
    
    # Get the referring page URL or default to product list
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/products/'))

def cart_detail(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass
    
    return render(request, 'cart/cart_detail.html', 
                 {'cart_items': cart_items, 'total': total, 'counter': counter})

def remove_from_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/cart/'))

def full_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/cart/'))

# views.py

def checkout(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        
        if not cart_items:
            messages.warning(request, "Your cart is empty")
            return redirect('cart_detail')
        
        if request.method == 'POST':
            if request.user.is_authenticated:
                name = request.user.username
                email = request.user.email
            else:
                name = "Guest"
                email = "guest@example.com"

            total1 = sum(item.product.price * item.quantity for item in cart_items)

            # Save order (order_number will be auto-generated)
            order = Order.objects.create(
                name=name,
                email=email,
                total=total1
            )

            # Save order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # Store in session for thank you page
            request.session['order_number'] = order.order_number
            request.session['order_total'] = str(total1)

            cart_items.delete()
            return redirect('thank_you')

        return render(request, 'cart/checkout.html')

    except ObjectDoesNotExist:
        messages.error(request, "There was an error with your checkout")
        return redirect('cart_detail')


def thank_you(request):
    order_number = request.session.get('order_number', 'ORD-000000')
    order_total = request.session.get('order_total', '0.00')
    
    context = {
        'order_number': order_number,
        'order_total': order_total,
        'estimated_delivery': "3-5 business days"
    }
    return render(request, 'cart/thank_you.html', context)


def my_orders(request):
    orders = Order.objects.all().order_by('-created')
    return render(request, 'cart/my_orders.html', {'orders': orders})


from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 'products/food.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'products/detail.html', {'product': product})