from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponseRedirect
from carts.models import Cartitem
from .forms import OrderForm,AddressForm
from .models import Order,OrderProduct,Payment
from store.models import Variation
import datetime
from django.template.context_processors import csrf
from django.urls import reverse
from orders.models import Address
from django.contrib.auth.decorators import login_required


def Payments(request):

    return render(request,'orders/payments.html')


def Order_Confirmation(request, order_number):
    # Retrieve the order details
    order = get_object_or_404(Order, order_number=order_number)

    # Pass the order details to the template
    context = {
        'order': order,
    }

    # Render the order confirmation template with the order details
    return render(request, 'orders/order_confirmation.html', context)
   
def Place_order(request, total=0, quantity=0):
    current_user = request.user

    # Retrieve cart items for the current user
    cart_items = Cartitem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    # If the cart is empty, redirect to the store
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Create a new order instance and populate it with form data
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total 
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20240405
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # Update product stock after successful order
            for cart_item in cart_items:
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()

            order=Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            context={
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }

            return render(request,'orders/payments.html',context)

    else:
        form = OrderForm()

    # Pass the form to the template
    context = {
        'form': form,
    }

    return render(request, 'orders/payments.html', context)

def Cash_on_delivery(request, order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)

    # Move the cart items to Order Product table
    cart_items = Cartitem.objects.filter(user=request.user)
    

    # Update product stock after successful order
    for cart_item in cart_items:
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()

    # Update the order status to indicate payment confirmation
    order.is_ordered = True
    order.save()

    # Update the order status to 'ACCEPTED'
    order.status = 'COMPLETED'
    order.save()
    
    

    #save the order details to orderproduct
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

    # Delete all the current user's cart items
    Cartitem.objects.filter(user=request.user).delete()

    # Render the confirm_payment.html template with the order details
    context = {
        'order_number': order_number,
        'order': order
    }
    return render(request, 'orders/order_confirmation.html', context)


def Add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('address_list')  # Redirect to address list view after adding address
    else:
        form = AddressForm()
    return render(request, 'orders/add_address.html', {'form': form})

def Edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('payments')  # Redirect to payments view after editing address
    else:
        form = AddressForm(instance=address)
    return render(request, 'orders/edit_address.html', {'form': form, 'address': address})

def Delete_address(request, address_id):
    address = get_object_or_404(Address, pk=address_id)
    if request.method == 'POST':
        address.delete()
        return redirect('checkout')  # Redirect to checkout view after deleting address
    return render(request, 'delete_address.html', {'address': address})

