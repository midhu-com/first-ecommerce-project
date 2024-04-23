from django.shortcuts import render, redirect
from .forms import RegistrationForm,UserForm,UserProfileForm
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from .models import Account,UserProfile
from carts.models import Cart,Cartitem
from carts.views import _cart_id
from orders.models import Order,OrderProduct
import requests
from django.shortcuts import get_object_or_404
from .models import Address
from .forms import AddressForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username=email.split("@")[0]
            
            Account = get_user_model()
            user = Account.objects.create_user(email=email, first_name=first_name, last_name=last_name, phone_number=phone_number, password=password,username=username)
            user.is_active = False
            user.save()
            # user activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            
            messages.success(request, 'Please confirm your email address to complete the registration')
            return redirect('login')  # Assuming you have a 'login' named URL pattern
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out.")
    return redirect('login')

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                
                cart = Cart.objects.get(cart_id=_cart_id(request))
            
                # Check if a cart item exists for the specified cart
                is_cart_item_exists = Cartitem.objects.filter(cart=cart).exists()
                
                if is_cart_item_exists:
                    # Retrieve the cart item associated with the specified cart
                    cart_item = Cartitem.objects.filter(cart=cart)

                    # getting the product variations by cart id
                    product_variation=[]
                    for item in cart_item:
                        variation=item.variations.all()
                        product_variation.append(list(variation))

                        # get the cart items from the user to access his product variations
                        cart_item=Cartitem.objects.filter(user=user)
                        ex_var_list=[]
                        id=[]
                        for item in cart_item:
                            existing_variation=item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)

                        for pr in product_variation:
                            if pr in ex_var_list:
                                index=ex_var_list.index(pr)
                                item_id=id[index]
                                item=Cartitem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user=user
                                item.save()
                            else:
                                cart_item=Cartitem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()

                    
                    
            except:
                
                # Handle the case where the cart does not exist
                pass  # Ignoring the error as cart might not exist for all users
            if user.is_superuser:
                return redirect('admin_view')
            else:
                auth.login(request, user)
                #messages.success(request, "You are logged in.")
                # when i add cart without login cleck checkout redirects to login afetr login it redirects to checkout page.for imp this use requesstss library.
                url=request.META.get('HTTP_REFERER')
                try:
                    query=requests.utils.urlparse(url).query
                    
                    #next=/carts/checkout/
                    params=dict(x.split('=')for x in query.split('&'))
                    if 'next' in params:
                        nextPage=params['next']
                        return redirect(nextPage)
                      
                except:
                    return redirect('dashboard')
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')
    return render(request, 'accounts/login.html')


# dashboard is only access when logged in

@login_required(login_url='login')
def dashboard(request):
    orders=Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count=orders.count()
    context={
        'orders_count':orders_count,
    }
    return render(request, 'accounts/dashboard.html',context)


def activate_account(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            # Your activation logic here
            return HttpResponse("Account activated successfully!")
        else:
            return HttpResponse("Invalid activation link!")
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist) as e:
        return HttpResponse("Invalid activation link!")
    

def forgotpassword(request):
    if request.method=='POST':
        email=request.POST['email']
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__exact=email)
            # reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            #to_email = form.cleaned_data.get('email')
            to_email=email
            #email = EmailMessage(mail_subject, message, to=[to_email])
            send_email=EmailMessage(mail_subject, message, to=[to_email])
            #email.send()
            send_email.send()
            messages.success(request,'Password reset email have been send to your email address.')
            return redirect('login')
        else:
            messages.error(request,'Account does not exist!')
            return redirect('forgotpassword')
        
    return render(request,'accounts/forgotpassword.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
        
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist) as e:
        user=None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,'Please reset your password')
        return redirect('resetpassword')
    else:
        messages.error(request,'this link have been expired')
        return redirect('login')
    
def resetpassword(request):
    if request.method=='POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']

        if password==confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'password reset successfully.')
            return redirect('login')
        else:
            messages.error(request,'password do not match!')
            return redirect('resetpassword')
    else:
         return render(request,'accounts/resetpassword.html')
    

# show the order details of the current user
def My_Orders(request):
    orders=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context={
        'orders': orders,
    }
    return render(request,'accounts/my_orders.html',context)

#edit the user profile details
@login_required
def Edit_profile(request):
    # Get the UserProfile instance for the current user
    userprofile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        #Populate the forms with the POST data and instances
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)

        # Check if both forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # Save both forms
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated')
            return redirect('edit_profile')  # Redirect to the same page after successful update
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        # If it's not a POST request, create forms with instances
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile':userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)

# generate invoice when click on order number at my order

@login_required(login_url='login')
def Order_detail(request,order_id):
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
    return render(request,'accounts/order_detail.html',context)


# user profile details
@login_required
def Profile(request):
    # Get the UserProfile instance for the current user
    userprofile = get_object_or_404(UserProfile, user=request.user)
    
    context = {
        
        'user_profile':userprofile,
    }
    return render(request, 'accounts/profile.html', context)


#Add new address/edit/delete/view.py

def AddressList(request):
    addresses = Order.objects.filter(user=request.user)
    return render(request, 'accounts/address_list.html', {'addresses': addresses})

def AddAddress(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('address_list')  # Redirect to address list view
    else:
        form = AddressForm()
    return render(request, 'accounts/add_address.html', {'form': form})

def EditAddress(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('payments')  # Redirect to address list view
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/edit_address.html', {'form': form, 'address': address})

def DeleteAddress(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    if request.method == 'POST':
        address.delete()
        return redirect('address_list')  # Redirect to address list view
    return render(request, 'delete_address.html', {'address': address})

