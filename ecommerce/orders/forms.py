from django import forms
from django.utils import timezone
from.models import Order,Coupon
from .models import Address
from store.models import Variation
from django.forms import modelformset_factory

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

    def clean_discount(self):
        print("clean dicound method called")
        discount = self.cleaned_data.get('discount')
        if discount is not None and discount < 0:
            raise forms.ValidationError("Coupon discount cannot be negative.")
        elif discount > 200:
            raise forms.ValidationError("Coupon discount limited to RS.200 for all coupons ")
            
        return discount

    def clean(self):
        cleaned_data = super().clean()
        valid_from = cleaned_data.get('valid_from')
        valid_to = cleaned_data.get('valid_to')

        if valid_to and valid_to <= timezone.now():
            self.add_error('valid_to', 'Valid to date cannot be in the past.')

        if valid_from and valid_to and valid_from > valid_to:
            self.add_error('valid_from', 'Valid from date cannot be later than valid to date.')

        return cleaned_data
        
class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        exclude = ['product'] 
        fields = ['id','variation_category', 'variation_value','stock', 'image', 'is_active']  

    def __init__(self, *args, **kwargs):
        super(VariationForm, self).__init__(*args, **kwargs)
        
        self.fields['variation_category'].widget.attrs.update({'class': 'form-control'})
        self.fields['variation_value'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['stock'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
VariationFormSet = modelformset_factory(Variation, form=VariationForm, extra=1, can_delete=True)
