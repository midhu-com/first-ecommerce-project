from django.shortcuts import render,redirect
from .models import Cart,Cartitem,wishlist
from store.models import Product
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from store.models import Variation
from django.contrib.auth.decorators import login_required
from accounts.models import Address
from django.contrib import messages
from django.http import JsonResponse
from orders.models import Coupon
import json
from django.utils import timezone


# Create your views here.

def _cart_id(request):   #_cart_id is a private function format
    cart =   request.session.session_key
    if not cart:        
        cart=request.session.create()
    return cart



def add_cart(request, product_id):
    current_user = request.user
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        color = request.POST.get('color')
        size = request.POST.get('size')

        # Retrieve active variations based on color and size
        try:
            color_variation = Variation.objects.get(product=product, variation_category='color', variation_value__iexact=color, is_active=True)
            size_variation = Variation.objects.get(product=product, variation_category='size', variation_value__iexact=size, is_active=True)

            # Check if variations have sufficient stock
            if color_variation.stock > 0 and size_variation.stock > 0:
                if current_user.is_authenticated:
                    existing_cart_item = Cartitem.objects.filter(
                        product=product,
                        user=current_user,
                        variations=color_variation,
                    ).filter(variations=size_variation).first()

                    if existing_cart_item:
                        if existing_cart_item.quantity + 1 > min(color_variation.stock, size_variation.stock):
                            messages.error(request, f"Sorry, the stock limit for this product ({color}, {size}) has been exceeded.")
                            return redirect('cart')
                        else:
                            existing_cart_item.quantity += 1
                            existing_cart_item.save()
                    else:
                        new_cart_item = Cartitem.objects.create(
                            product=product,
                            quantity=1,
                            user=current_user,
                        )
                        new_cart_item.variations.add(color_variation, size_variation)
                        new_cart_item.save()

                else:
                    try:
                        cart = Cart.objects.get(cart_id=_cart_id(request))
                    except Cart.DoesNotExist:
                        cart = Cart.objects.create(cart_id=_cart_id(request))
                        cart.save()

                    existing_cart_item = Cartitem.objects.filter(
                        product=product,
                        cart=cart,
                        variations=color_variation,
                    ).filter(variations=size_variation).first()

                    if existing_cart_item:
                        if existing_cart_item.quantity + 1 > min(color_variation.stock, size_variation.stock):
                            messages.error(request, f"Sorry, the stock limit for this product ({color}, {size}) has been exceeded.")
                            return redirect('cart')
                        else:
                            existing_cart_item.quantity += 1
                            existing_cart_item.save()
                    else:
                        new_cart_item = Cartitem.objects.create(
                            product=product,
                            quantity=1,
                            cart=cart,
                        )
                        new_cart_item.variations.add(color_variation, size_variation)
                        new_cart_item.save()

            else:
                messages.error(request, f"Sorry, the selected variations ({color}, {size}) are out of stock.")
                return redirect('cart')

        except Variation.DoesNotExist:
            messages.error(request, "Selected variation not found.")
            return redirect('cart')

    return redirect('cart')

# remove the product from the cart
def remove_cart(request,product_id,cart_item_id):
    
    product=get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item=Cartitem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_item=Cartitem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity>1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')    

#remove cart item from cart
def remove_cart_item(request,product_id,cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = get_object_or_404(Cartitem, product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = get_object_or_404(Cartitem, product=product, cart=cart, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

        messages.success(request, "Item removed from cart.")
    except Cart.DoesNotExist:
        messages.error(request, "Cart not found.")
    except Cartitem.DoesNotExist:
        messages.error(request, "Cart item not found.")
    
    return redirect('cart')


# create cart page
def cart(request,total=0,quantity=0,cart_items=None):

    total = 0
    quantity = 0
    tax = 0
    grand_total = 0
    cart_items = []
    try:
        
        if request.user.is_authenticated:
            cart_items=Cartitem.objects.filter(user=request.user,is_active=True)
        else:

            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=Cartitem.objects.filter(cart=cart,is_active=True)

        for cart_item in cart_items:
            total+=(cart_item.product.price_after_discount() * cart_item.quantity)
            quantity+=cart_item.quantity

             # Fetch stock information for each variation associated with the cart item
            stock_info = cart_item.stock_info

            # Add stock information to cart item (optional, for context)
            cart_item.stock_info_dict = stock_info

        tax=(2 * total)/100
        grand_total=total + tax

    except ObjectDoesNotExist:
        pass # just ignore
        #cart_items=[]  Initialize cart_items as an empty list if the cart doesn't exist

    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,

    }
    return render(request,'store/cart.html',context)

# checkout page
@login_required(login_url='login')
def checkout(request,total=0,quantity=0,cart_items=None):
    try:
        tax = 0
        grand_total = 0
        selected_address = None

        # Check if the user has saved billing address details
            
        billing_address = Address.objects.filter(user=request.user)

        if request.method == 'POST':
            selected_address_id = request.POST.get('selected_address')
            if selected_address_id:
                selected_address = get_object_or_404(Address,id=selected_address_id)

        if request.user.is_authenticated:
            cart_items=Cartitem.objects.filter(user=request.user,is_active=True)

           
        else:

            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=Cartitem.objects.filter(cart=cart,is_active=True)

        for cart_item in cart_items:
            total+=(cart_item.product.price * cart_item.quantity)
            quantity+=cart_item.quantity

        tax=(2 * total)/100
        grand_total=total + tax

    except ObjectDoesNotExist:
        pass # just ignore
        #cart_items=[]  Initialize cart_items as an empty list if the cart doesn't exist

    context={
        'total': total,
        'quantity': quantity,
        'cart_items':cart_items,
        'tax':tax,  
        'grand_total':grand_total,
        'billing_address':billing_address,# Pass the billing address to the template
        'selected_address':selected_address,
    }
    return render(request,'store/checkout.html',context)




@login_required(login_url='login')
def Wishlist(request):  
    if request.method == 'POST':
        wishlist_item_id = request.POST.get('wishlist_item_id')
        if wishlist_item_id:
            wishlist_item = get_object_or_404(wishlist, id=wishlist_item_id)
            wishlist_item.delete()
            return redirect('wishlist')
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = wishlist.objects.filter(user=request.user).count()
    else:
        wishlist_count = 0

    wishlist_items = wishlist.objects.filter(user=request.user)
    
    context = {
        'wishlist_items': wishlist_items,
        'wishlist_count':wishlist_count,
    }
    return render(request, 'store/wishlist.html',context)


# add product to wishlist
def Add_wishlist(request, product_slug):
    try:
        product = Product.objects.get(slug=product_slug)
        color_variation = None
        size_variation = None 
        # Get the selected variations from the request
        if request.method == "POST":
            color_variation_id = request.POST.get('color_variation')
            size_variation_id = request.POST.get('size_variation')
            try:
                if color_variation_id:
                    color_variation = Variation.objects.get(id=color_variation_id)
                if size_variation_id:
                    size_variation = Variation.objects.get(id=size_variation_id)
            except Variation.DoesNotExist:
                pass
        # Create the Wishlist item with the selected variations
        if request.user.is_authenticated:
            user_instance = request.user
            wishlist_item, created = wishlist.objects.get_or_create(user=user_instance, product=product)

            # Set variations for the wishlist item
            if color_variation:
                wishlist_item.color_variation = color_variation
            if size_variation:
                wishlist_item.size_variation = size_variation
            wishlist_item.save()

            return redirect('wishlist')  # Redirect to the wishlist page after adding the product
        else:
            return redirect('login')  # Redirect to the login page if user is not authenticated

    except Product.DoesNotExist:
        return redirect('store')  # Redirect to home page if the product doesn't exist

def Remove_wishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(wishlist, id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')


def product_detaill(request, product_slug):
    try:
        single_product = Product.objects.get(slug=product_slug)
        in_cart = Cartitem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        
        in_wishlist = wishlist.objects.filter(user=request.user, product=single_product).exists()
       
        
    except Exception as e:
        raise e
    
    
    context = {
        'single_product': single_product,
        'in_cart' : in_cart,
        'in_wishlist': in_wishlist,
        
    }
    return render(request, 'store/product_detail.html',context)
def apply_coupon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code')

        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True)
            # Apply the coupon logic here, such as calculating discounts, etc.
            # Example:
            # discount_amount = calculate_discount(coupon, ...)
            return JsonResponse({'message': 'Coupon applied successfully', 'discount_amount': coupon.discount})
        except Coupon.DoesNotExist:
            return JsonResponse({'message': 'Invalid coupon code. Please check and try again.'}, status=400)
        except Exception as e:
            return JsonResponse({'message': 'Failed to apply coupon. Please try again.'}, status=400)

    return JsonResponse({'message': 'Invalid request method'}, status=405)


def get_coupons(request):
    current_date = timezone.now()
    coupons = Coupon.objects.filter(valid_from__lte=current_date, valid_to__gte=current_date, active=True)
    coupons_list = [{'code': coupon.code, 'discount': coupon.discount} for coupon in coupons]
    return JsonResponse({'coupons': coupons_list})

