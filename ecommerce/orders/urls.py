from django.urls import path
from .import views
urlpatterns = [
   
    path('payments/', views.Payments, name='payments'),
    path('place_order/', views.Place_order, name='place_order'),
    path('order_confirmation/<str:order_number>/', views.Order_Confirmation, name='order_confirmation'),
    path('cash_on_delivery/<str:order_number>/', views.Cash_on_delivery, name='cash_on_delivery'),
   
   
    path('order_complete/', views.Order_complete, name='order_complete'),
    path('cancel_order/<int:order_number>/', views.cancell_order, name='cancel_order'),
    path('order_return/<int:order_number>/',views.order_return,name='order_return'),

    path('add_to_wallet/<int:order_number>/',views.add_to_wallet,name='add_to_wallet'),
   
   
    

]

   
   

    
    
