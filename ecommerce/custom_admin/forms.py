from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.models import User
from django import forms
from category.models import Category
from store.models import Product,Image
from accounts.models import Account



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

   