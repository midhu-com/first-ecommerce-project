from django import forms

from.models import Order,Coupon
from .models import Address

class OrderForm(forms.ModelForm):
    class Meta:
        model=Order
        fields=['first_name','last_name','phone','email','address_line_1','address_line_2','country','state','city','order_note']



class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name', 'last_name','email', 'phone','address_line_1', 'address_line_2', 'city', 'state', 'country', ]

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code','discount','valid_from','valid_to']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'valid_to': forms.DateTimeInput(attrs={'class': 'form-control'}),
        }
        