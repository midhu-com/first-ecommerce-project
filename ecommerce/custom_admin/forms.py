from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.models import User
from django import forms
from category.models import Category
from store.models import Product,Image
from accounts.models import Account
from orders.models import ProductOffers,CategoryOffers,Coupon
from category.models import Category
from django.utils import timezone



class RegisterUser(UserCreationForm):
    class Meta:
        model = User
        fields = ["username","email","password1","password2","is_superuser"]

class EditForm(UserChangeForm):
    password=None
    class Meta:
        model= User
        fields = ["username","email","is_superuser"]
        widgets = {
            "username":forms.TextInput(attrs={'class':'form-control'}),
            "email":forms.EmailInput(attrs={'class':'form-control'}),

        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'slug','description','cat_image']  # Include all the fields you want to display in the form

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['created_date', 'modified_date']  # Exclude these fields from the form
        fields = ['product_name','slug','description', 'price','stock','is_available','category']
        widgets={
            'product_name':forms.TextInput(attrs={'class':'form-control'}),
            'slug':forms.TextInput(attrs={'class':'form-control'}),
            'description':forms.TextInput(attrs={'class':'form-control'}),
            'price':forms.NumberInput(attrs={'class':'form-control'}),
            'stock':forms.NumberInput(attrs={'class':'form-control'}),
            'is_available':forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'category':forms.Select(attrs={'class':'form-select'}),
            
            
            }
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Query the Category model to get all categories
        self.fields['category'].queryset = Category.objects.all() 
        # Set initial value for category if it exists
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance.category:
                self.initial['category'] = instance.category.pk

class ProductImageForm(forms.ModelForm)   :
    images=forms.FileField(widget=forms.TextInput(attrs={
        "name":"images",
        "type":"File",
        "class":"form-control",
        "multiple":"True",
    }),label="")

    class Meta:
        model=Image
        fields=['images']


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon  
        fields = '__all__'

    def clean_valid_to(self):
        valid_to = self.cleaned_data.get('valid_to')
        if valid_to and valid_to > timezone.now().date():
            raise forms.ValidationError("Valid to date cannot be in the past.")
        return valid_to

    def clean(self):
        cleaned_data = super().clean()
        valid_from = cleaned_data.get('valid_from')
        valid_to = cleaned_data.get('valid_to')
        if valid_from and valid_to:
            if valid_to <= valid_from:
                raise forms.ValidationError("Valid to date must be later than valid from date.")
        return cleaned_data


class ProductOfferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductOfferForm, self).__init__(*args, **kwargs)
        # Filter products to include only active ones
        self.fields['product'].queryset = Product.objects.filter(is_available=True)

    class Meta:
        model = ProductOffers
        fields = '__all__'  # You can customize the fields as needed

class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffers
        fields = '__all__'  # You can customize the fields as needed
   