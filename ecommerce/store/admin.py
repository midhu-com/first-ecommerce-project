from django.contrib import admin
from .models import Product,Image

# Register your models here.

class ImageInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = Image

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=('product_name','price','stock','category','modified_date','is_available')
    prepopulated_fields={'slug':('product_name',)}
    inlines=[ImageInline]

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass



   