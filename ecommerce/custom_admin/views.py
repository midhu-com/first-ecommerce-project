from django.shortcuts import render,redirect
from django.contrib import messages
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
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from orders.forms import CouponForm
from orders.models import Coupon
from django.utils.timezone import make_aware
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

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the logging level as per your requirement
logger = logging.getLogger(__name__)



# Create your views here.
def admin_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        #Redirect to login page if user is not authenticated or not an admin
        return redirect('login')

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
    context={
        'orders_list':orders_list,
        }
    
    return render(request,'customadmin/orders.html',context)

def Coupon_view(request):
    # Query all listed categories
    coupon_list = Coupon.objects.all()

    # Prepare user data to pass to the template
    context={'coupon_list':coupon_list}
    
    return render(request,'customadmin/coupons.html',context)


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
@login_required(login_url='login')
def logout_view(request):
    auth.logout(request)
    messages.success(request, "You are logged out.")
    return redirect('index')

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

def order_returnn(request,order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)
    
    # Update order status to 'Cancelled' and set is_ordered to False
    order.status = 'Returned'
    order.is_ordered = False
    order.save()

    # Retrieve order items and update product stock
    order_items = OrderProduct.objects.filter(order=order)
    for order_item in order_items:
        product = order_item.product
        product.stock += order_item.quantity  # Increase product stock
        product.save()
    messages.success(request, "Order has been returned successfully.")
    return redirect('my_orders')  # Redirect to a success page after cancellation


# coupon logic is here
def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Coupon created successfully')
            return redirect('coupons')
            
    else:
        form = CouponForm()
    
    return render(request,'customadmin/add_coupon.html',{'form':form})

def edit_coupon(request,coupon_id):
    coupon = get_object_or_404(Coupon,id=coupon_id)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request,'Coupon updated successfully')
            return redirect('coupons')
            
    else:
        form = CouponForm(instance=coupon)
    
    return render(request,'customadmin/edit_coupon.html',{'form':form,'coupon':coupon})

def delete_coupon(request,coupon_id):
    coupon = get_object_or_404(Coupon,id=coupon_id)
    coupon.delete()
    messages.success(request,'Coupon deleted successfully')
    return redirect('coupon')


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
        # Check if start_date is before end_date
 

    orders = Order.objects.filter(created_at__date__range=[start_date, end_date]).order_by('-created_at')



    droporders = Order.objects.filter(    Q(status='Returned') | Q(status='Cancelled'),
               created_at__date__range=[start_date, end_date] )


    total_sales = orders.aggregate(total_sales=Sum('final_total'))['total_sales'] or 0
    total_drop_sales = droporders.aggregate(total_drop_sales=Sum('final_total'))['total_drop_sales'] or 0
    #total_discount = orders.aggregate(total_discount=Sum('discount_value'))['total_discount'] or 0
    total_sales_count = orders.aggregate(total_sales_count=Count('id'))['total_sales_count'] or 0
    total_coupons = orders.aggregate(total_coupons=Count('coupon'))['total_coupons'] or 0
    net_sales = total_sales - total_coupons-total_drop_sales

    return {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        #'total_discount': total_discount,
         'total_sales_count': total_sales_count,
        'total_coupons': total_coupons,
        'net_sales': net_sales,
        'orders': orders,'total_drop_sales':total_drop_sales
    }





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
        sales_data = context.get('sales_data', [])
   
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












