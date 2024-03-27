from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,Http404
from.models import Product
from category.models import Category
from carts.views import _cart_id
from carts.models import Cartitem

# Create your views here.
def store(request,category_slug=None):
    categories=None
    products=None

    if category_slug != None:
        categories =get_object_or_404(Category,slug=category_slug)
        products   =Product.objects.filter(category=categories,is_available=True)
        product_count=products.count()
    else:
        products=Product.objects.all().filter(is_available=True)
        product_count=products.count()

    context={
        'products':products,
        'product_count':product_count,
    }
    return render(request,'store/store.html',context)


# product desccription 
def product_detail(request,category_slug,product_slug):
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        product_images = single_product.product_images.all()  # Assuming you have a related name 'images' for the image field
       # in_cart=Cartitem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
        
        
    except Product.DoesNotExist:
        raise Http404("Product does not exist")
    context = {
        'single_product': single_product,
        'product_images': product_images, 
        #'in_cart':in_cart,
    }
    return render (request,'store/product_detail.html',context)