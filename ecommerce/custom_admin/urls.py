from django.urls import path
from .import views


urlpatterns=[
    path('',views.admin_view,name='admin_view'),
   
    path('users/',views.user_view,name='users'),
    path('products/',views.products_view,name='products'),
    path('categories/',views.category_view,name='categories'),
    path('add/',views.add_category,name='add_category'),
    path('add_product/',views.add_product,name='add_product'),
    path('add_category/',views.add_category,name='add_category,'),
    path('success/',views.success_page,name='success_page'),
    path('logout/',views.logout_view,name='logout_view'),
    path('block/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('edit_category<int:category_id>/', views.edit_category, name='edit_category'),


    
    
   



    
    
]