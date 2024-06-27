from django.urls import path
from .import views

urlpatterns=[
    path('',views.cart,name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),

   
    
    path('wishlist/', views.Wishlist, name='wishlist'),
    path('add_wishlist/<slug:product_slug>/', views.Add_wishlist, name='add_wishlist'),
    path('remove_wishlist/<int:wishlist_item_id>/', views.Remove_wishlist, name='remove_wishlist'),
    path('product_detaill/<slug:product_slug>/', views.product_detaill, name='product_detaill'),

    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('get-coupons/', views.get_coupons, name='get_coupons'),
    
    
    
]
