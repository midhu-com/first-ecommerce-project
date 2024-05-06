from django.contrib import admin
from .models import Payment,Order,OrderProduct,Coupon
# Register your models here.

admin.site.register(Order)

admin.site.register(OrderProduct)

admin.site.register(Payment)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'valid_from', 'valid_to']
    search_fields = ['code']
    list_filter= ['valid_from', 'valid_to']
