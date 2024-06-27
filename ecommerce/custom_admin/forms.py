from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.models import User
from django import forms
from category.models import Category
from store.models import Product,Image
from orders.models import ProductOffers,CategoryOffers,Coupon
from category.models import Category



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
        error_messages = {
            'price': {
                'min_value': "Price cannot be negative."
            },
            'stock': {
                'min_value': "Stock cannot be negative."
            }
            # Add more error messages as needed for other fields
        }
       
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Query the Category model to get all categories
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        # Set initial value for category if it exists
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance.category:
                self.initial['category'] = instance.category.pk

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0.01:
            raise forms.ValidationError(self.Meta.error_messages['price']['min_value'])
        return price  # Only return the cleaned price if validation passes

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError(self.Meta.error_messages['stock']['min_value'])
        return stock

class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = 'custom_clearable_file_input.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['multiple'] = True  # Allow multiple files to be selected
        return context
class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = 'custom_clearable_file_input.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['multiple'] = True  # Allow multiple files to be selected
        return context

class ProductImageForm(forms.ModelForm):
    images = forms.FileField(widget=CustomClearableFileInput(attrs={
        'class': 'form-control-file',
    }), label='Product Images', required=False)

    class Meta:
        model = Image
        fields = ['images']

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            images = self.cleaned_data.get('images')
            for image in images:
                if image:
                    img_instance = Image(image=image, product=instance.product)
                    img_instance.save()
                    # Perform cropping logic here if needed
        
        return instance

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon  
        fields = ['code','discount','valid_from', 'valid_to']

    

class ProductOfferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductOfferForm, self).__init__(*args, **kwargs)
        # Filter products to include only active ones
        self.fields['product'].queryset = Product.objects.filter(is_available=True)

    class Meta:
        model = ProductOffers
        fields = '__all__'  # You can customize the fields as needed

    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage  < 0:
            raise forms.ValidationError("Offer value cannot be negative.")
        if discount_percentage > 50:
            raise forms.ValidationError("Offer value percentage cannot be more than 50%.")
        return discount_percentage
       

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be after end date.")
        return cleaned_data

class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffers
        fields = '__all__'  # You can customize the fields as needed

    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage < 0:
            raise forms.ValidationError("Offer value cannot be negative.")
        if discount_percentage > 50:
            raise forms.ValidationError("Offer value percentage cannot be more than 50%.")
        return discount_percentage

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be after end date.")
        return cleaned_data
