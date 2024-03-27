from django.shortcuts import render,redirect
from .models import Cart,Cartitem
from django.shortcuts import redirect
from store.models import Product
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

# Create your views here.

def _cart_id(request):   #_cart_id is a private function format
    cart =   request.session.session_key
    if not cart:        
        cart=request.session.create()
    return cart

def add_cart(request,product_id):   
    product=Product.objects.get(id=product_id) # to get the product
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request)) # get the cart usng _cat_id present in the session
    except Cart.DoesNotExist:
        cart=Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()

    try:
        cart_item=Cartitem.objects.get(product=product,cart=cart)
        cart_item.quantity+=1  #cart_item.quantity=cart_item.quantity+1
        cart_item.save()
    except Cartitem.DoesNotExist:
        cart_item=Cartitem.objects.create(
            product=product,
            quantity=1,
            cart=cart,

        )
        cart_item.save()
    
    return redirect('cart')

# remove the product from the cart
def remove_cart(request,product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    cart_item=Cartitem.objects.get(product=product,cart=cart)
    if cart_item.quantity>1:
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')    


def remove_cart_item(request,product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    cart_item=Cartitem.objects.get(product=product,cart=cart)
    cart_item.delete()
    return redirect('cart')

def cart(request,total=0,quantity=0,cart_items=None):
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=Cartitem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total+=(cart_item.product.price * cart_item.quantity)
            quantity+=cart_item.quantity
        tax=(2 * total)/100
        grand_total=total + tax
    except cart.ObjectNotExist:
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