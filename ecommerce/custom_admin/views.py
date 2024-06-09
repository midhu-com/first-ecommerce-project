from django.shortcuts import render,redirect
from django.contrib import messages
from accounts.models import Account
from category.models import Category
from store.models import Product
from store.models import Image,Variation
from .forms import ProductForm,ProductImageForm,CategoryForm,CouponForm
from django.shortcuts import get_object_or_404
import logging
from django.shortcuts import render, redirect
from .forms import CategoryForm,CouponForm,ProductOfferForm,CategoryOfferForm
from orders.models import Order,OrderProduct,Payment
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from orders.forms import CouponForm,VariationForm
from orders.models import Coupon,CategoryOffers,ProductOffers
from datetime import datetime
from django.http import HttpResponse
from django.db.models import Sum,Q,Count
import csv
from django.utils import timezone
from django.utils import timezone as tz
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponseBadRequest
from django.views.decorators.cache import never_cache
from django import forms    
import calendar
import json
from django.forms import inlineformset_factory




# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the logging level as per your requirement
logger = logging.getLogger(__name__)

def superuser_required(view_func):
    """
    Decorator for views that checks if the user is a superadmin,
    redirects to the login page if not.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superadmin:  # Custom attribute
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')  # Redirect to the login page or any other page
    return _wrapped_view

@never_cache
@login_required(login_url='login')

def admin_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login')
    else:
        filter_period = 'monthly'
        best_selling_products = Product.objects.annotate(total_quantity_sold=Sum('orderproduct__quantity')).exclude(total_quantity_sold=None).order_by('-total_quantity_sold')[:10]
        best_selling_categories = Category.objects.annotate(total_quantity_sold=Sum('product__orderproduct__quantity')).exclude(total_quantity_sold=None).order_by('-total_quantity_sold')[:10]

        if 'period' in request.GET:
            filter_period = request.GET['period']

        end_date = datetime.now().date()
        if filter_period == 'weekly':
            start_date = end_date - timedelta(days=7)
        elif filter_period == 'monthly':
            start_date = end_date.replace(day=1)
        elif filter_period == 'yearly':
            start_date = end_date.replace(day=1, month=1)

        if filter_period == 'weekly':
            date_range = [start_date + timedelta(days=i) for i in range(7)]
        elif filter_period == 'monthly':
            _, last_day = calendar.monthrange(start_date.year, start_date.month)
            date_range = [start_date.replace(day=1) + timedelta(days=i) for i in range(last_day)]
        elif filter_period == 'yearly':
            date_range = [start_date.replace(month=i, day=1) for i in range(1, 13)]

        orders = Order.objects.filter(created_at__range=[start_date, end_date])
        droporders = Order.objects.filter(Q(status='Returned') | Q(status='Cancelled'), created_at__date__range=[start_date, end_date])
        total_sales = orders.aggregate(total_sales=Sum('final_total'))['total_sales'] or 0
        total_drop_sales = droporders.aggregate(total_drop_sales=Sum('final_total'))['total_drop_sales'] or 0
        total_discount = orders.aggregate(total_discount=Sum('coupon_discount'))['total_discount'] or 0
        total_coupons = orders.aggregate(total_coupons=Count('coupon'))['total_coupons'] or 0
        net_sales = total_sales - total_coupons - total_drop_sales

        sales_data = {date: sum(order.final_total if order.final_total is not None else 0 for order in orders if order.created_at.date() == date) for date in date_range}

        monthly_total_sales = {}
        monthly_total_count = {}
        if filter_period == 'yearly':
            for month in range(1, 13):
                month_orders = [order for order in orders if order.created_at.month == month]
                month_sales = sum(order.final_total if order.final_total is not None else 0 for order in month_orders)
                month_count = sum(1 for order in month_orders)
                monthly_total_sales[month] = month_sales
                monthly_total_count[month] = month_count

        sorted_sales_data = sorted(sales_data.items())
        sorted_dates = [date.strftime('%Y-%m-%d') for date, _ in sorted_sales_data]
        sorted_total_values = [value for _, value in sorted_sales_data]

        if filter_period == 'yearly':
            chart_data = {
                'labels': list(monthly_total_sales.keys()),
                'data': [str(value) for value in monthly_total_sales.values()]
            }
        else:
            chart_data = {
                'labels': sorted_dates,
                'data': [float(value) for value in sorted_total_values]  # Convert Decimal to float
        }

        order_count_data = {date: sum(1 for order in orders if order.created_at.date() == date) for date in date_range}
        sorted_order_count_data = sorted(order_count_data.items())
        sorted_order_dates = [date.strftime('%Y-%m-%d') for date, _ in sorted_order_count_data]
        sorted_order_counts = [count for _, count in sorted_order_count_data]

        if filter_period == 'yearly':
            orders_chart_data = {
                'labels': list(monthly_total_count.keys()),
                'data': list(monthly_total_count.values())
            }
        else:
            orders_chart_data = {
                'labels': sorted_order_dates,
                'data':  [int(count) for count in sorted_order_counts]  # Convert Decimal to int if needed
            }

        context = {
            'chart_data': json.dumps(chart_data),
                'orders_chart_data': json.dumps(orders_chart_data),
            'filter_period': filter_period,
            'best_selling_products': best_selling_products,
            'best_selling_categories': best_selling_categories,
        }

    return render(request, 'customadmin/custom_admin_home.html', context)
   

# To display the user details
@never_cache  
@login_required(login_url='login')                
def user_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login')
    else:
        # Query all registered users
        registered_users = Account.objects.all()

        # Prepare user data to pass to the template
        context={'registered_users':registered_users}
    
    return render(request,'customadmin/users.html', context)

# To dissplay the product details
@never_cache
@login_required(login_url='login')  
def products_view(request):
    if request.user.is_superuser:
       
    
        # Query all listed products
        product_list = Product.objects.all()

        # Prepare user data to pass to the template
        context={'product_list':product_list}
    else:
        return redirect('login')
    
    return render(request,'customadmin/products.html',context)

# To dissplay the category details
@never_cache
@login_required(login_url='login')  
def category_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login')
    else:
        # Query all listed categories
        category_list = Category.objects.all()

        # Prepare user data to pass to the template
        context={'category_list':category_list}
    
    return render(request,'customadmin/categories.html',context)

# To display the order details


@login_required(login_url='login') 
def Orders_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login')
    else:
        # Query all registered users
        orders_list = Order.objects.all().order_by('-created_at')
        payment = Payment.objects.all()
    
        # Prepare user data to pass to the template
        context={
            'orders_list':orders_list,
            'payment':payment,
            }
    
    return render(request,'customadmin/orders.html',context)

# To display the coupon details
@never_cache
@login_required(login_url='login')
def Coupon_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login')
    else:
        # Query all listed categories
        coupon_list = Coupon.objects.all()

        # Prepare user data to pass to the template
        context={'coupon_list':coupon_list}
    
    return render(request,'customadmin/coupons.html',context)




#add new category
@never_cache
@login_required(login_url='login')
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('categories')  # Assuming 'category_list' is the name of the URL pattern for viewing all categories
    else:
        form = CategoryForm()
    return render(request, 'customadmin/add_category.html', {'form': form})


        
#logout view

@superuser_required
def logout_view(request):
    auth.logout(request)
    messages.success(request, "You are logged out.")
    return redirect('login')

# success page after add products
@never_cache
def success_page(request):
    
    return render(request, 'customadmin/success.html')

# Admin have the permission to block & unblock the user
@never_cache
def block_user(request, user_id):
    account = Account.objects.get(id=user_id)
    account.is_active = False  # Block the user
    account.save()
    messages.success(request, f"{account.username} has been blocked.")
    return redirect('admin_view')  # Redirect back to the custom admin page

@never_cache
def unblock_user(request, user_id):
    account= Account.objects.get(pk=user_id)
    if not account.is_active:
        account.is_active = True  # Unblock the user
        account.save()
        messages.success(request, f"{account.username} has been unblocked.")
    else:
        messages.error(request, f"{account.username} is already unblocked.")
    return redirect('admin_view')  # Redirect back to the custom admin page

@never_cache
@login_required(login_url='login')
def add_product(request):
    productform=ProductForm()
    imageform=ProductImageForm()

    if request.method == 'POST':
        files=request.FILES.getlist('images')
        productform = ProductForm(request.POST,request.FILES)

        if productform.is_valid():
            product=productform.save(commit=False)
            category = productform.cleaned_data['category']
            if category.is_active:
                product.save()
                for file in files:
                    Image.objects.create(product=product,image=file)
                messages.success(request, 'Product added successfully')
                return redirect('products')
            else:
                messages.error(request, 'Cannot add product to an inactive category')
        else:
            messages.error(request, 'Please correct the errors below!')
            
    context={"form":productform,"form_image":imageform}
    return render(request, 'customadmin/add_product.html',context)

# edit & delete product details

@never_cache
@login_required
def delete_product(request,product_id):
    if request.method == 'POST':
        product=get_object_or_404(Product,id=product_id)
    # Soft delete the product by setting is_active to False
        product.is_available=False
        product.save()
        logger.info(f"Product {product_id} soft deleted by user {request.user.id}")
        return redirect('products')

    return redirect('products')
@never_cache

def restore_product(request,product_id):
    if request.method == 'POST':
        product=get_object_or_404(Product,id=product_id)
    # restore the product after delete setting is_active to True
        product.is_available=True
        product.save()
        logger.info(f"Product {product_id} restored by user {request.user.id}")
        return redirect('products')@never_cache
    

# add variations like color and size to products   
@login_required(login_url='login')
def add_variation(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    VariationFormSet = inlineformset_factory(Product, Variation, form=VariationForm, extra=1, can_delete=True)

    if request.method == 'POST':
        formset = VariationFormSet(request.POST, instance=product)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Variations added successfully')
            return redirect('products')
        else:
            print(formset.errors)  # Print the formset errors to the console for debugging
            for form in formset:
                print(form.errors)  # Print the formset errors to the console for debugging
            messages.error(request, 'Please correct the errors below!')
    else:
        formset = VariationFormSet(instance=product)
    
    context = {
        'product': product,
        'formset': formset,
    }
    return render(request, 'customadmin/add_variation.html', context)

   


    
@never_cache  
@login_required(login_url='login') 
def edit_product(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    product_form = ProductForm(request.POST, instance=product)
    image_form = ProductImageForm(request.POST,request.FILES)
    
    if request.method == 'POST':
        
        product_form = ProductForm(request.POST, instance=product)
        image_form = ProductImageForm(request.POST,request.FILES)
    
        if product_form.is_valid():
            category = product_form.cleaned_data['category']
            if category.is_active:
                product = product_form.save()

                # Save the images
                for file in request.FILES.getlist('images'):
                    Image.objects.create(product=product,image=file)

                messages.success(request, 'Product edited successfully')
                return redirect('products')  # Redirect after successful form submission
            else:
                messages.error(request, 'Cannot assign product to an inactive category')
        else:
            # Log the form errors
           
            #logger.error(product_form.errors)  # You need to define the logger variable
            messages.error(request, "Form contains errors. Please correct them.")
    else:
        product_form = ProductForm(instance=product)
        image_form = ProductImageForm()
        
    
    return render(request, 'customadmin/edit_product.html', {
        'product_form': product_form, 'product': product,'image_form':image_form
        })


#edit,delete & restore category details
@never_cache
def delete_category(request,category_id):
    
    category = get_object_or_404(Category, id=category_id)
    if category:
        category.is_active = False
        category.save()
        messages.success(request, 'Category deleted successfully')
    else:
        messages.error(request, 'Category does not exist')
    
    return redirect('categories')
    
def restore_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if category:
        category.is_active = True
        category.save()
        messages.success(request, 'Category restored successfully')
    else:
         messages.error(request, 'Category does not exist')
    return redirect('categories')


@never_cache
@login_required(login_url='login')
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST,request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect('categories')  # Redirect to the category list page after successful update
        else:
            messages.success(request, 'Please correct the errors below!')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'customadmin/edit_category.html', {'form': form, 'category': category})


# coupon logic is here to create new coupons add & delete coupons
@ never_cache
@login_required(login_url='login')
def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            print("Form data:", form.cleaned_data) 
            coupon = form.save(commit=False)
            coupon.save()
            messages.success(request,'Coupon created successfully')
            return redirect('coupons')
        else:
            messages.error(request, 'Failed to add coupon. Please correct the errors.')
            
    else:
        form = CouponForm()
    
    return render(request,'customadmin/add_coupon.html',{'form':form})

@never_cache
@login_required(login_url='login')
def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully.')
            return redirect('coupons')
        else:
            messages.error(request, 'Failed to update coupon. Please enter valid date.')
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'customadmin/edit_coupon.html', {'form': form, 'coupon': coupon})

@never_cache
def delete_coupon(request,coupon_id):
    coupon = get_object_or_404(Coupon,id=coupon_id)
    coupon.delete()
    messages.success(request,'Coupon deleted successfully')
    return redirect('coupons')


@never_cache
@login_required(login_url='login')
def Invoice(request, order_id):
    # Use get_object_or_404 to retrieve the order, which will automatically handle the DoesNotExist exception
    order = get_object_or_404(Order, id=order_id)
    order_detail = OrderProduct.objects.filter(order__id=order_id)
    
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    
    # Fetching payment method from the related Payment object
    payment_method = order.payment.payment_method if order.payment else None

    # Retrieve coupon discount
    coupon_discount = 0
    if order.coupon:
        try:
            coupon = Coupon.objects.get(code=order.coupon)
            # Check if the coupon is valid
            if coupon.valid_from <= order.created_at <= coupon.valid_to:
                coupon_discount = coupon.discount
        except Coupon.DoesNotExist:
            pass
     # Assuming tax is a percentage value stored in the order
    tax = (2 * subtotal) / 100
    
    
    # Calculate final total
    final_total = subtotal + tax - coupon_discount

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
        'coupon_discount': coupon_discount,
        'final_total':final_total,
        'payment': order.payment,
        'payment_method': payment_method,
    }
    return render(request, 'customadmin/invoice.html', context)


# method to generate sales report

def generate_sales_report_data(period, start_date=None, end_date=None):
    today = timezone.now().date()
    orders = Order.objects.none()

    if period == 'daily':
        start_date = today
        end_date = today
    elif period == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'monthly':
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif period == 'custom' and start_date and end_date:
        # Parse start_date and end_date if provided
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date.")
    
        # Check if start_date is before end_date
 

    orders = Order.objects.filter(created_at__date__range=[start_date, end_date]).order_by('-created_at')



    droporders = Order.objects.filter(    Q(status='Returned') | Q(status='Cancelled'),
               created_at__date__range=[start_date, end_date] )


    total_sales = orders.aggregate(total_sales=Sum('final_total'))['total_sales'] or 0
    total_drop_sales = droporders.aggregate(total_drop_sales=Sum('final_total'))['total_drop_sales'] or 0
    total_discount = orders.aggregate(total_discount=Sum('coupon_discount'))['total_discount'] or 0
    total_sales_count = orders.aggregate(total_sales_count=Count('id'))['total_sales_count'] or 0
    total_coupons = orders.aggregate(total_coupons=Count('coupon'))['total_coupons'] or 0
    net_sales = total_sales - total_coupons-total_drop_sales

    return {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'total_drop_sales':total_drop_sales,
        'total_discount': total_discount,
        'total_sales_count': total_sales_count,
        'total_coupons': total_coupons,
        'net_sales': net_sales,
        'orders': orders,'total_drop_sales':total_drop_sales
    }


@login_required(login_url='login')
def sales_report(request, period=None):
    if request.method == 'POST':
        period = request.POST.get('period')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        try:
            context = generate_sales_report_data(period, start_date, end_date)
            sales_data = context.get('sales_data', [])
        except ValueError as e:
            return HttpResponseBadRequest(str(e))
    else:
        if period not in ['daily', 'weekly', 'monthly', 'yearly', 'custom']:
            period = 'daily'
        context = generate_sales_report_data(period)
        
   
    return render(request, 'customadmin/sales_report.html', context)





def render_sales_report_pdf(report_data):
    html = render_to_string('sales_report_pdf.html', report_data)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response


def render_sales_report_excel(report_data):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xls"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer', 'Total Value', 'Discount', 'Net Value', 'Created At'])
    for order in report_data['orders']:
        writer.writerow([
            order.id,
            order.user.get_username(),
            order.original_total_value,
            order.discounted_total,
     
            order.created_at
        ])

    return response

    

@never_cache
def download_sales_report_pdf(request, period=None):
    if request.method == 'POST':
        period = request.POST.get('period')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
    else:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

    # Validate if both start_date and end_date are provided
    if period == 'custom' and (not start_date or not end_date):
        return HttpResponseBadRequest('Missing start_date or end_date parameters for custom period')

    # Generate report data based on the period and dates
    report_data = generate_sales_report_data(period, start_date, end_date)
    
    # Debug print statements for start_date and end_date
    print("Start Date:", start_date)
    print("End Date:", end_date)

    # Check if period parameter is missing in report_data
    if not report_data.get('period'):
        return HttpResponseBadRequest('Missing period parameter in report data')

    # Render the PDF report using the generated data
    return render_sales_report_pdf(report_data)


def sales_report_excel(request, period=None):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    report_data = generate_sales_report_data(period, start_date, end_date)
    return render_sales_report_excel(report_data)

# admin have tyhe prmission to change the orrder status peding->processing->shiporder->deliverd
@never_cache
@login_required(login_url='login')
def admin_change_order_status(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    new_status = request.POST.get('new_status')

    if new_status in dict(Order.STATUS):
        order.status = new_status
        order.save()
        messages.success(request, f"Order #{order.order_number} status updated to {new_status}")
    else:
        messages.error(request, "Invalid order status")

    return redirect('orders')
    

@never_cache
@login_required(login_url='login')
def admin_cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if order.cancel_order():    
        messages.success(request, f"Order #{order.order_number} has been canceled")
    else:
        messages.error(request, f"Unable to cancel order #{order.order_number}")

    return redirect('orders')

@never_cache
@login_required(login_url='login')
def admin_return_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if order.return_order():    
        messages.success(request, f"Order #{order.order_number} has been returned")
    else:
        messages.error(request, f"Unable to return order #{order.order_number}")

    return redirect('orders')

@never_cache
@login_required(login_url='login')
def admin_ship_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if order.ship_order():
        messages.success(request, f"Order #{order.order_number} has been shipped")
       
    else:
        messages.error(request, f"Unable to ship order #{order.order_number}")
        

    return redirect('orders')

@never_cache
@login_required(login_url='login')
def admin_deliver_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if order.deliver_order():
        messages.success(request, f"Order #{order.order_number} has been delivered")
    else:
        messages.error(request, f"Unable to deliver order ship first #{order.order_number}")

    return redirect('orders')


# productoffer module create,edit  & delete
@never_cache
@login_required(login_url='login')
def product_offer_create(request):
    if request.method == 'POST':
        form = ProductOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_offers_list')  # Change 'admin_homepage' to the appropriate URL
    else:
        form = ProductOfferForm()
    return render(request, 'customadmin/product_offer_create.html', {'form': form})

@never_cache
@login_required(login_url='login')
def product_offer_edit(request, pk):
    offer = get_object_or_404(ProductOffers, pk=pk)
    if request.method == 'POST':
        form = ProductOfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('product_offers_list')  # Change 'admin_homepage' to the appropriate URL
    else:
        form = ProductOfferForm(instance=offer)
    return render(request, 'customadmin/product_offer_edit.html', {'form': form})

@never_cache
def product_offer_delete(request, pk):
    offer = get_object_or_404(ProductOffers, pk=pk)
    offer.delete()
    return redirect('product_offers_list')  # Change 'admin_homepage' to the appropriate URL
  

#category offer create,edit & delete.
@ never_cache
@login_required(login_url='login')
def category_offer_create(request):
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_offers_list')  # Change 'admin_homepage' to the appropriate URL
    else:
        form = CategoryOfferForm()
    return render(request, 'customadmin/category_offer_create.html', {'form': form})

@never_cache
@login_required(login_url='login')
def category_offer_edit(request, pk):
    offer = get_object_or_404(CategoryOffers, pk=pk)
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('category_offers_list')  # Change 'admin_homepage' to the appropriate URL
    else:
        form = CategoryOfferForm(instance=offer)
    return render(request, 'customadmin/category_offer_edit.html', {'form': form})

@never_cache
def category_offer_delete(request, pk):
    offer = get_object_or_404(CategoryOffers, pk=pk)
    offer.delete()
    return redirect('category_offers_list')  # Change 'admin_homepage' to the appropriate URL

# list the product and category offer details
@never_cache
@login_required(login_url='login')
def list_product_offers(request):
    # Retrieve all product offers from the database
    product_offers = ProductOffers.objects.all()
    return render(request, 'customadmin/product_offers_list.html', {'product_offers': product_offers})

@never_cache
@login_required(login_url='login')
def list_category_offers(request):
    # Retrieve all category offers from the database
    category_offers = CategoryOffers.objects.all()
    return render(request, 'customadmin/category_offers_list.html', {'category_offers': category_offers})

@never_cache
def offers(request):

    return render(request, 'customadmin/offers.html')

@never_cache
@login_required(login_url='login')
def product_detailad(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)

    product_offer = product.offer if hasattr(product, 'offer') else None
    category_offers = product.Category.offer if hasattr(product.Category, 'offer') else None
    
    context = {
        'product': product,
        'product_offer': product_offer,
        'category_offers': category_offers,
        # Add other context variables as needed (e.g., related products, reviews)
    }

    return render(request, 'customadmin/product_detail.html', context)


@never_cache
@login_required(login_url='login')
def category_detailad(request, category_pk):
    category = get_object_or_404(Category, pk=category_pk)
    # Optionally fetch related products:
    products = Product.objects.filter(Category=category)
    context = {'category': category, 'products': products}
    return render(request, 'customadmin/category_detail.html', context)






