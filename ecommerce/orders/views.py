from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse
from carts.models import Cartitem
from .forms import OrderForm,AddressForm
from .models import Order,OrderProduct,Payment
from store.models import Variation
import datetime
from django.template.context_processors import csrf
from django.urls import reverse
from orders.models import Address
from store.models import Product
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def Payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user,is_ordered=False, order_number=body['orderID'])
    
    # tore tranmsaction detaisl inside payment model
    payment=Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status=body['status'],
    )
    payment.save()
    
    order.payment = payment
    order.is_ordered=True
    order.save()

    #move the cart item to orderproduct table
    cart_items=Cartitem.objects.filter(user=request.user)
    
    for item in cart_items:
        orderproduct=OrderProduct()
        orderproduct.order_id=order.id
        orderproduct.payment=payment
        orderproduct.user_id=request.user.id
        orderproduct.product_id=item.product_id
        orderproduct.quantity=item.quantity
        orderproduct.product_price=item.product.price
        orderproduct.ordered=True
        orderproduct.save()

        cart_item=Cartitem.objects.get(id=item.id)
        product_variation=cart_item.variations.all()
        orderproduct=OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        # reduce the quantity from stock when place an order
        #product=Product.objects.get(id=item.product_id)
        #product.stock -=item.quantity
        #product.save()

    #clear the cart items
    Cartitem.objects.filter(user=request.user).delete()

    # send an order receiver email to the user
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order':order,
        
    })
    #to_email = form.cleaned_data.get('email')
    to_email=request.user.email
    #email = EmailMessage(mail_subject, message, to=[to_email])
    send_email=EmailMessage(mail_subject, message, to=[to_email])
    #email.send()
    send_email.send()

    #send order number and transaction id to sendData method
    data = {
        'order_number':order.order_number,
        'transID':payment.payment_id,
    }
    return JsonResponse(data) 



    #return render(request,'orders/payments.html')


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
    if request.method == 'POST':
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

        selected_address_id=request.POST.get('selected_address')

        if selected_address_id:
            selected_address=get_object_or_404(Address,id=selected_address_id)
    
            order=Order.objects.create(
                user = current_user,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                email=current_user.email,
                phone=current_user.phone_number,
                address_line_1=selected_address.address_line_1,
                city=selected_address.city,
                state=selected_address.state,
                country=selected_address.country,
                order_total = grand_total ,
                tax = tax,
                ip = request.META.get('REMOTE_ADDR'),

            )
             # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20240405
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()  
            
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
            return HttpResponse("Please select an addresss")
    

    else:
       
        return render(request, 'orders/payments.html')
            

            

def Cash_on_delivery(request, order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)

    # Move the cart items to Order Product table
    cart_items = Cartitem.objects.filter(user=request.user)
    

    # Update product stock after successful order
    #for cart_item in cart_items:
        #product = cart_item.product
        #product.stock -= cart_item.quantity
        #product.save()

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

def cancel_orderr(request, order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)
    
    # Update order status to 'Cancelled' and set is_ordered to False
    order.status = 'Cancelled'
    order.is_ordered = True
    order.save()

    # Retrieve order items and update product stock
    order_items = OrderProduct.objects.filter(order=order)
    for order_item in order_items:
        product = order_item.product
        product.stock += order_item.quantity  # Increase product stock
        product.save()
    messages.success(request, "Order has been cancelled successfully.")
    return redirect('my_orders')  # Redirect to a success page after cancellation

def Order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id = order.id)
        payment= Payment.objects.get(payment_id=transID)

        context = {
           
           'order':order,
           'ordered_products':ordered_products,
           'order_number':order.order_number,
           'transID':payment.payment_id,
           'payment':payment,
        } 
        return render(request,'orders/order_complete.html',context)
    except(Payment.DoesNotExist,Order.DoesNotExist):
        redirect('home')

    




