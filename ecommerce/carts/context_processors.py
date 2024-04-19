from .models import Cart, Cartitem
from .views import _cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))  # Assuming cart_id is unique
            if request.user.is_authenticated:
                cart_items = Cartitem.objects.all().filter(user=request.user)
                #cart_items = Cartitem.objects.all().filter(cart=cart[:1])
                
            else:
                cart_items = Cartitem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count= cart_count) # Return the dictionary
