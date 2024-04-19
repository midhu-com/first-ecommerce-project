from django.urls import path
from.import views

urlpatterns=[ 
    path('register/',views.register,name='register'),
    path('login/',views.user_login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('',views.dashboard,name='dashboard'),

    path('activate/<uidb64>/<token>/',views.activate_account,name='activate_account'),
    path('forgotpassword/',views.forgotpassword,name='forgotpassword'),  
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,name='resetpassword_validate'),  
    path('resetpassword/',views.resetpassword,name='resetpassword'), 

    path('my_orders/',views.My_Orders,name='my_orders'),
    path('edit_profile/',views.Edit_profile,name='edit_profile'),

    path('order_detail/<int:order_id>/',views.Order_detail,name='order_detail'),
    
    
    
    ]
    
   
            