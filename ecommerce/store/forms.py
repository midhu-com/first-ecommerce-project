from django import forms
from .models import ReviewRating,Image

class ReviewForm(forms.ModelForm):
    class Meta:
        model=ReviewRating
        fields  =['subject','review','rating']

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = '__all__'  # Adjust as needed based on desired fields