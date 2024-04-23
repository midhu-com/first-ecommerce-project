from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import logout
from accounts.models import Account
from category.models import Category
from store.models import Product
from store.models import Image
from .forms import ProductForm,ProductImageForm,CategoryForm
from django.shortcuts import get_object_or_404
import logging
from django.shortcuts import render, redirect
from .forms import CategoryForm
from orders.models import Order,OrderProduct

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the logging level as per your requirement
logger = logging.getLogger(__name__)



# Create your views here.
def admin_view(request):
     return render(request, 'customadmin/base.html')
                   
def user_view(request):
    # Query all registered users
    registered_users = Account.objects.all()

    # Prepare user data to pass to the template
    context={'registered_users':registered_users}
    
    return render(request,'customadmin/users.html', context)


def products_view(request):
    # Query all listed products
    product_list = Product.objects.all()

    # Prepare user data to pass to the template
    context={'product_list':product_list}
    
    return render(request,'customadmin/products.html',context)


def category_view(request):
    # Query all listed categories
    category_list = Category.objects.all()

    # Prepare user data to pass to the template
    context={'category_list':category_list}
    
    return render(request,'customadmin/categories.html',context)


def Orders_view(request):
    # Query all registered users
    orders_list = Order.objects.all()
    


    # Prepare user data to pass to the template
    context={'orders_list':orders_list}
    
    return render(request,'customadmin/orders.html',context)


def Invoice(request,order_id):
    order_detail=OrderProduct.objects.filter(order__order_number=order_id)
    order=Order.objects.get(order_number=order_id)
    subtotal=0
    for i in order_detail:
        subtotal +=i.product_price * i.quantity
    context={
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal,
    }
    return render(request,'customadmin/invoice.html',context)



#add new category
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('categories')  # Assuming 'category_list' is the name of the URL pattern for viewing all categories
    else:
        form = CategoryForm()
    return render(request, 'customadmin/add_category.html', {'form': form})

# add  new product details 
def add_product(request):
    productform=ProductForm()
    imageform=ProductImageForm()

    if request.method == 'POST':
        files=request.FILES.getlist('images')
        productform = ProductForm(request.POST,request.FILES)

        if productform.is_valid():
            product=productform.save(commit=False)
            product.save()
            print(request,"product created successfully")

            for file in files:
                Image.objects.create(product=product,image=file)
            return redirect('products')  # Redirect to the product list page after successful submission
            
    context={"form":productform,"form_image":imageform}
    return render(request, 'customadmin/add_product.html',context)

#logout view
def logout_view(request):
    logout(request)
    return redirect('login')

# success page after add products
def success_page(request):
    
    return render(request, 'customadmin/success.html')

def block_user(request, user_id):
    account = Account.objects.get(id=user_id)
    account.is_active = False  # Block the user
    account.save()
    messages.success(request, f"{account.username} has been blocked.")
    return redirect('admin_view')  # Redirect back to the custom admin page

def unblock_user(request, user_id):
    account= Account.objects.get(pk=user_id)
    if not account.is_active:
        account.is_active = True  # Unblock the user
        account.save()
        messages.success(request, f"{account.username} has been unblocked.")
    else:
        messages.error(request, f"{account.username} is already unblocked.")
    return redirect('admin_view')  # Redirect back to the custom admin page

# edit & delete product details


def delete_product(request,product_id):
    if request.method == 'POST':
        product=get_object_or_404(Product,id=product_id)
    # Soft delete the product by setting is_active to False
        product.is_active=False
        product.save()
        return redirect('products')
    else:
        return redirect('products')
    

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product edited successfully')
            return redirect('admin_view')  # Redirect after successful form submission
        else:
            # Log the form errors
            print(form.errors)
            logger.error(form.errors)  # You need to define the logger variable
            messages.error(request, "Form contains errors. Please correct them.")
    else:
        form = ProductForm(instance=product)  # Pass the product instance to pre-fill the form
    
    return render(request, 'customadmin/edit_product.html', {'form': form, 'product': product})


#edit  & delete category details

def delete_category(request,category_id):
    category=get_object_or_404(Category,id=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('categories')
        category.is_active=False
        category.save()
    else:
        return redirect('categories')

def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect('categories')  # Redirect to the category list page after successful update
    else:
        form = CategoryForm(instance=category)

    return render(request, 'customadmin/edit_category.html', {'form': form, 'category': category})

def Order_cancel(request, order_id):
    # Get the order object from the database
    order = get_object_or_404(Order, pk=order_id)
    
    # Check if the order belongs to the current user or if the user has permission to cancel orders
    if request.user == order.user or request.user.has_perm('your_app.cancel_order'):
        # Cancel the order (you may need to implement a method on your Order model to update the status)
        order.status = 'Cancelled'
        order.save()
        # Optionally, you can add a message to indicate that the order has been canceled
        messages.success(request, "Order has been canceled successfully.")
    else:
        # If the user does not have permission to cancel the order, display an error message
        messages.error(request, "You do not have permission to cancel this order.")
    
    # Redirect back to the orders page or any other appropriate URL
    return redirect('orders')












