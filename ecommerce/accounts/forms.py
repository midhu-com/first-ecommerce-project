from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .models import Account,UserProfile,Address

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
       widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'class': 'form-control'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
    )

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='Enter first Name'
        self.fields['last_name'].widget.attrs['placeholder']='Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder']='Enter phone number'
        self.fields['email'].widget.attrs['placeholder']='Enter email address'
        
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

class UserForm(forms.ModelForm):
    class Meta:
        model=Account
        fields=('first_name','last_name','phone_number')   

    def __init__(self,*args,**kwargs):
        super(UserForm,self).__init__(*args,**kwargs) 
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture=forms.ImageField(required=False,error_messages={'invalid':("Image files only")},widget=forms.FileInput)
    class Meta:
        model=UserProfile
        fields = ('address_line_1','address_line_2','city','state','country','profile_picture')

    def __init__(self,*args,**kwargs):
        super(UserProfileForm,self).__init__(*args,**kwargs) 
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name','last_name','email','phone_number','address_line_1','address_line_2', 'city', 'state', 'country']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['address_line_1'].widget.attrs.update({'class': 'form-control'})
        self.fields['address_line_2'].widget.attrs.update({'class': 'form-control'})
        self.fields['city'].widget.attrs.update({'class': 'form-control'})
        self.fields['state'].widget.attrs.update({'class': 'form-control'})
        self.fields['country'].widget.attrs.update({'class': 'form-control'})