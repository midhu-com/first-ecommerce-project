from django.contrib import admin
from .models import Cart,Cartitem,wishlist
# Register your models here.


class CartAdmin(admin.ModelAdmin):
    list_display=('cart_id','date_added')

class CartItemAdmin(admin.ModelAdmin):
    list_display=('product','cart','quantity','is_active')

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'date_added')  # Display these fields in the admin list
    list_filter = ('user', 'date_added')  # Add filters for these fields
    search_fields = ['user_username', 'product_product_name']  # Add search functionality for related fields


admin.site.register(wishlist,WishlistAdmin)
admin.site.register(Cart,CartAdmin)
admin.site.register(Cartitem,CartItemAdmin)

