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

            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
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
            if user.is_superuser:
                return redirect('admin_view')
            else:
                auth.login(request, user)
                messages.success(request, "You are logged in.")
                return redirect('index')  # Assuming 'home' is a valid URL name
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