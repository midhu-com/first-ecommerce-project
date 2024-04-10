from django.shortcuts import render,redirect
from .models import Cart,Cartitem
from django.shortcuts import redirect
from store.models import Product
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from store.models import Variation
from django.db.models import F
from django.contrib.auth.decorators import login_required

# Create your views here.

def _cart_id(request):   #_cart_id is a private function format
    cart =   request.session.session_key
    if not cart:        
        cart=request.session.create()
    return cart



def add_cart(request,product_id): 
    product=Product.objects.get(id=product_id) # to get the product 
    product_variation=[]

#extract variations from the
    if request.method=='POST':
        for item in request.POST:
            key = item
            value=request.POST[key]
            
            try:
                variation=Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
                
            except:
                pass
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request)) # get the cart usng _cat_id present in the session
    except Cart.DoesNotExist:
        cart=Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()

    # Check if a cart item with the same product and variations exists
    existing_cart_item = Cartitem.objects.filter(product=product, cart=cart)

    # Filter existing cart items by variations
    for variation in product_variation:
        existing_cart_item = existing_cart_item.filter(variations=variation)

    existing_cart_item = existing_cart_item.first()

    if existing_cart_item:
        # If an existing cart item with the same variations is found, increase its quantity
        existing_cart_item.quantity += 1
        existing_cart_item.save()
    else:
        # If no existing cart item is found, create a new cart item
        new_cart_item = Cartitem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        new_cart_item.variations.add(*product_variation)
        """if product_variation in ex_var_list:
            #increase the cart_item_quantity
            index=ex_var_list.index(product_variation)
            item_id=id[index]
            item=Cartitem.objects.get(product=product,id=item_id)
            item.quantity+=1
            item.save()
        else:
            #create new cart_item
            item=Cartitem.objects.create(product=product,cart=cart,quantity=1)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
    else: 
        cart_item=Cartitem.objects.create( product=product, quantity=1,cart=cart,)
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()"""
    return redirect('cart')



# remove the product from the cart
def remove_cart(request,product_id,cart_item_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    try:
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
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    cart_item=Cartitem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

# create cart page
def cart(request,total=0,quantity=0,cart_items=None):
    try:
        tax = 0
        grand_total = 0
        #if request.user.is_authenticated:
            #cart_items=Cartitem.objects.filter(user=request.user,is_active=True)
        #else:

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
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
    }
    return render(request,'store/checkout.html',context)