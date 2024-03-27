from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import logout
from accounts.models import Account
from category.models import Category
from store.models import Product
from store.models import Image
from .forms import ProductForm,ProductImageForm
from django.shortcuts import get_object_or_404



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
    # Query all registered users
    product_list = Product.objects.all()

    # Prepare user data to pass to the template
    context={'product_list':product_list}
    
    return render(request,'customadmin/products.html',context)


def category_view(request):
    # Query all registered users
    category_list = Category.objects.all()

    # Prepare user data to pass to the template
    context={'category_list':category_list}
    
    return render(request,'customadmin/categories.html',context)

from django.shortcuts import render, redirect
from .forms import CategoryForm


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
    print("product id is:",product)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products')  # Redirect after successful form submission
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
    category = get_object_or_404(Category, pk=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('categories')  # Redirect to the product list page after successful update
    else:
        form = ProductForm(instance=category)

    return render(request, 'customadmin/edit_category.html', {'form': form, 'product':category})













