from django.shortcuts import render, redirect
from .forms import RegistrationForm
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
from .models import Account
from carts.models import Cart,Cartitem
from carts.views import _cart_id


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
                is_cart_item_exists = Cartitem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = Cartitem.objects.filter(cart=cart)
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
                return redirect('index')  
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

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