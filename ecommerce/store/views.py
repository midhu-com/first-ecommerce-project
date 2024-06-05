from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect,Http404
from.models import Product,ReviewRating
from category.models import Category
from carts.views import _cart_id
from carts.models import Cartitem
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct,ProductOffers,CategoryOffers
from carts.models import wishlist
from store.models import Product




# Create your views here.
def store(request,category_slug=None):
    categories=None
    products=None

    if category_slug != None:
        categories =get_object_or_404(Category,slug=category_slug)
        products   =Product.objects.filter(category=categories,is_available=True).order_by('id')
        paginator=Paginator(products,10)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=products.count()
    else:
        products=Product.objects.filter(is_available=True).order_by('id')
        paginator=Paginator(products,8)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=products.count()

    context={
        'products':paged_products,
        'product_count':product_count,
    }
    return render(request,'store/store.html',context)


# product desccription 
def product_detail(request,category_slug,product_slug):
   
    try:
        
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)

        product_offer = ProductOffers.objects.filter(product=single_product).first()
        category_offer = CategoryOffers.objects.filter(category=single_product.category).first()

        product_discount_amount = (single_product.price * product_offer.discount_percentage) / 100 if product_offer else 0
        category_discount_amount = (single_product.price * category_offer.discount_percentage) / 100 if category_offer else 0

        if product_discount_amount >= category_discount_amount:
            highest_discount_amount = product_discount_amount
            highest_offer = product_offer
        else:
            highest_discount_amount = category_discount_amount
            highest_offer = category_offer

        disc_price = single_product.price - highest_discount_amount


        product_images = single_product.product_images.all()  # Assuming you have a related name 'images' for the image field
        in_cart=Cartitem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
        if request.user.is_authenticated:
            in_wishlist=wishlist.objects.filter(user=request.user.id,product=single_product).exists()
        else:
            in_wishlist = False
        
    except Product.DoesNotExist:
        raise Http404("Product does not exist")
    orderproduct = None
   
    if request.user.is_authenticated:

        try:
            orderproduct=OrderProduct.objects.filter(user=request.user,product=single_product)
        except OrderProduct.DoesNotExist:
           pass
    
    
   

    # get the review
    reviews=ReviewRating.objects.filter(product_id=single_product.id,status=True)
    
    context = {
        'single_product': single_product,
        'product_images': product_images, 
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        'in_wishlist':in_wishlist, #success_message ':success_message ,
        'disc_price':disc_price,
        'highest_offer': highest_offer,
        'highest_discount_amount': highest_discount_amount,
        'product_discount_amount': product_discount_amount,
        'category_discount_amount': category_discount_amount,
        
    }
   
    return render (request,'store/product_detail.html',context)

def search(request):
    products = Product.objects.none()
    product_count=0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)).order_by('-created_date')
            product_count=products.count()

        # sorting
        sort_by=request.GET.get('sort_by')
        if sort_by =='price_low_high':
            products = products.order_by('price')

        elif sort_by == 'price_high_low':
            products = products.order_by('-price')
    context={
        'products':products,
        'product_count':product_count,
    }

    return render(request,'store/store.html',context)

def Submit_review(request,product_id):
    url=request.META.get('HTTP_REFERER','/')
    if request.method == 'POST':
        try:
            reviews=ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form=ReviewForm(request.POST,instance=reviews)
            form.save()
            messages.success(request,"Thankyou! Your reviews has been updated. ")
           

        except ReviewRating.DoesNotExist:
            form=ReviewForm(request.POST)
            if form.is_valid():
                data =  form.save(commit=False)
                data.subject=form.cleaned_data['subject']
                data.review=form.cleaned_data['review']
                data.rating=form.cleaned_data['rating']
                data.ip=request.META.get('REMOTE_ADDR')
                data.product_id=product_id
                data.user_id=request.user.id
                data.save()
                messages.success(request,"Thankyou! Your reviews has been submitted. ")
        return HttpResponseRedirect(url)
    else:
            # If not a POST request, redirect to the referrer URL
        return HttpResponseRedirect(url)