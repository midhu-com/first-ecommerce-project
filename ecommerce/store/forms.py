from django import forms
from .models import ReviewRating,Image

class ReviewForm(forms.ModelForm):
    class Meta:
        model=ReviewRating
        fields  =['subject','review','rating']
class MultipleFileInput(forms.ClearableFileInput):
    template_name = 'django/forms/widgets/clearable_multiple_file_input.html'
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs'].update({'multiple': True})
        return context

class ImageForm(forms.ModelForm):
    images = forms.FileField(widget=MultipleFileInput(attrs={
        'class': 'form-control-file',
    }), label='Product Images', required=False)

    
    
    class Meta:
        model = Image
        fields = ['images']
