from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse
from carts.models import Cartitem
from .forms import CouponForm
from .models import Order,OrderProduct,Payment,Coupon,Wallet
from store.models import Variation
from carts.models import Cart
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
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from xhtml2pdf import pisa  # Import the module from xhtml2pdf

def Payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user,is_ordered=False, order_number=body['orderID'])
    
    # store tranmsaction detaisl inside payment model
    payment=Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        payment_status=body['payment_status'],
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
        product=Product.objects.get(id=item.product_id)
        product.stock -=item.quantity
        product.save()

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
   
from django.shortcuts import redirect

def Place_order(request, total=0, quantity=0):
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_user = request.user
            selected_address_id = request.POST.get('selected_address')

            # Retrieve the coupon code from the form
            coupon_code = request.POST.get('coupon_code')
            discount_value = 0
            final_total = 0
            try:
                # retrive the users wallet and get the wallet balance
                wallet = Wallet.objects.get(user=current_user)
                wallet_balance = wallet.balance
            #If the user doesn't have a wallet,set wallet balance =0
            except Wallet.DoesNotExist:
                wallet_balance = 0


            # Retrieve cart items for the current user
            cart_items = Cartitem.objects.filter(user=current_user)
            cart_count = cart_items.count()

            # If the cart is empty, redirect to the store
            if cart_count <= 0:
                return redirect('store')

            grand_total = 0
            tax = 0
            final_total = 0
            for cart_item in cart_items:
                total += cart_item.product.price * cart_item.quantity
                quantity += cart_item.quantity

            tax = (2 * total) / 100
            grand_total = total + tax

            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    current_datetime = timezone.now()
                    if coupon.valid_from <= current_datetime <= coupon.valid_to:
                        discount_value = coupon.discount
                        print("Discount value:",discount_value)
                        final_total = Decimal(str(grand_total)) - discount_value
                        # Ensure final_total is not negative
                        final_total = max(0, final_total)
                       
                    else:
                        discount_value = 0
                        final_total = grand_total
                        messages.warning(request,"Coupon is invalid")
                        return redirect('checkout')
                except Coupon.DoesNotExist:
                    discount_value = 0
                    final_total = grand_total
                    messages.error(request,"Coupon Does Not Exist")
                    return redirect('checkout')

            if selected_address_id:
                selected_address = get_object_or_404(Address, id=selected_address_id)

                order = Order.objects.create(
                    user=current_user,
                    first_name=current_user.first_name,
                    last_name=current_user.last_name,
                    email=current_user.email,
                    phone=current_user.phone_number,
                    address_line_1=selected_address.address_line_1,
                    city=selected_address.city,
                    state=selected_address.state,
                    country=selected_address.country,
                    coupon=coupon_code,
                    order_total=grand_total,
                    coupon_discount=discount_value,
                    final_total=final_total,  # Assign the Decimal value
                    tax=tax,
                    ip=request.META.get('REMOTE_ADDR'),
                )

                # Generate order number
                current_datetime = timezone.now()
                yr = current_datetime.year
                mt = current_datetime.month
                dt = current_datetime.day
                d = datetime(yr, mt, dt)
                current_date = d.strftime("%Y%m%d")
                order_number = current_date + str(order.id)
                order.order_number = order_number
                order.save()

                order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

                context = {
                    'order': order,
                    'cart_items': cart_items,
                    'total': total,
                    'tax': tax,
                    'grand_total': grand_total,
                    'discount_value': discount_value,
                    'final_total': final_total,
                    'wallet_balance':wallet_balance,
                }

                return render(request, 'orders/payments.html', context)
            else:
                # check the user is selecteed an address before proceeding order
                messages.error(request,"Please select an address")
                return redirect('checkout')
            
        else:
            # Handle case where user is not authenticated
            return redirect('login')
    else:
        return redirect('checkout')

            

            

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

    # Update the order status to 'processing'
    order.status = 'Processing'
    order.payment_status = 'pending'
    order.payment_method = 'COD'
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



def Order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        # Update the order status to 'Completed'
        order.status = 'processing'
        order.payment_status = 'completed'
        order.save()

        ordered_products = OrderProduct.objects.filter(order_id = order.id)
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment= Payment.objects.get(payment_id=transID)

        context = {
           
           'order':order,
           'ordered_products':ordered_products,
           'order_number':order.order_number,
           'transID':payment.payment_id,
           'payment':payment,
           'subtotal':subtotal,
        } 
        return render(request,'orders/order_complete.html',context)
    except(Payment.DoesNotExist,Order.DoesNotExist):
        redirect('home')


def cancell_order(request, order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)
    
    # Retrieve the final_total from the Order model
    final_total = order.final_total

    if order.status == 'processing':
        # Retrieve order items and update product stock
        order_items = OrderProduct.objects.filter(order=order)
        for order_item in order_items:
            product = order_item.product
            product.stock += order_item.quantity  # Increase product stock
            product.save()

        # Update order status to 'Cancelled' and set is_ordered to False
        order.status = 'Cancelled'
        order.is_ordered = False
        order.save()

        # Refund payment and update wallet balance
        if order.payment_status == 'Completed':
            # Retrieve the user's wallet if it exists, or create a new wallet if it doesn't exist
            wallet, created = Wallet.objects.get_or_create(user=request.user)

            # Update wallet balance
            if created:
                wallet.balance = final_total
            else:
                wallet.balance += final_total
            wallet.save()

            # Update payment status to 'Refunded'
            order.payment_status = 'Refunded'
            order.payment.save()

            messages.success(request, "Order has been cancelled successfully. The paid amount is added to your wallet")
        else:
            messages.warning(request, "Order cancellation failed. Payment not completed.")

    return redirect('my_orders')

def order_return(request, order_number):
    # Retrieve the order based on the order number
    order = get_object_or_404(Order, order_number=order_number)
    
    final_total = order.final_total

    if order.status == 'Delivered':
        # Retrieve order items and update product stock
        order_items = OrderProduct.objects.filter(order=order)
        for order_item in order_items:
            product = order_item.product
            product.stock += order_item.quantity  # Increase product stock
            product.save()

        # Update order status to 'Returned' and set is_ordered to False
        order.status = 'Returned'
        order.is_ordered = False
        order.save()

        # Retrieve the user's wallet if it exists, or create a new wallet if it doesn't exist
        wallet, created = Wallet.objects.get_or_create(user=request.user)

        # Update wallet balance
        if created:
            wallet.balance = final_total
        else:
            wallet.balance += final_total
        wallet.save()

        messages.success(request, "Order has been returned successfully. The paid amount is added to your wallet.")
    else:
        messages.warning(request, "Order return failed. Order status is not 'Delivered'.")

    return redirect('my_orders')  # Redirect to a success page after return



def create_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('coupon_list') # shows the list of coupons
    else:
        form = CouponForm()
    return render(request, 'create_coupon.html', {'form': form})


def add_to_wallet(request, order_number):
    try:
        # Retrieve the user's wallet
        wallet = Wallet.objects.get(user=request.user)

        # Retrieve the order based on the order number
        order = Order.objects.get(order_number=order_number)

        # Retrieve the final total from the order
        final_total = order.final_total

        if wallet.balance < final_total:
            messages.error(request, "Insufficient balance in your wallet!")
            return redirect('cart')

        # Reduce the final total amount from the wallet balance
        wallet.balance -= final_total
        wallet.save()
       

        # Update the order status to completed
        order.status = 'processing'
        order.is_ordered = True
        order.save()

        # Retrieve the cart items and add them to the order
        cart_items = Cartitem.objects.filter(user=request.user)
        for item in cart_items:
            #save the order details to orderproduct
        
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

        # Update product stock after successful order
        for cart_item in cart_items:
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()

        # Redirect to order confirmation page with order details
        messages.success(request, "Order placed successfully. Amount deducted from your wallet")
        return redirect('order_confirmation', order_number=order.order_number)
    except ObjectDoesNotExist:
        messages.error(request, "An error occurred while processing your order.")
        return redirect('cart')


def generate_invoice_pdf(request, order_id):
    # Fetch the order details and other necessary data
    order = Order.objects.get(id=order_id)
    order_detail = OrderProduct.objects.filter(order=order)

    # Assuming order.final_total is a Decimal object
    total_value = order.final_total

    # Calculate GST if necessary
    gst = total_value - (total_value / Decimal('1.03'))

    # Calculate Subtotal
    subtotal = sum(item.product_price * item.quantity for item in order_detail)

    # Calculate Coupon Discount if any
    coupon_discount = order.coupon_discount if hasattr(order, 'coupon_discount') else Decimal('0.00')

    # Render the invoice HTML template with the order data
    rendered_html = render_to_string('invoice_template.html', {
        'order': order,
        'order_detail': order_detail,
        'subtotal': subtotal,
        'order.tax': order.tax,
        'coupon_discount': coupon_discount,
        'order.final_total': order.final_total,
        'gst': gst,
    })

    # Create an HttpResponse object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'

    # Convert the rendered HTML to PDF and write to the response
    pisa_status = pisa.CreatePDF(rendered_html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors with code %s' % pisa_status.err)
    
    return response








    




