from django.urls import path
from.import views

urlpatterns=[ 
    path('register/',views.register,name='register'),
    path('login/',views.user_login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('activate/<uidb64>/<token>/',views.activate_account,name='activate_account'),
    
    
    
    ]

   
            