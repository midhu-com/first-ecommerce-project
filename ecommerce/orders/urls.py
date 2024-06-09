from django.urls import path
from .import views
urlpatterns = [
   
    path('payments/', views.Payments, name='payments'),
    path('place_order/', views.Place_order, name='place_order'),
    path('order_confirmation/<str:order_number>/', views.Order_Confirmation, name='order_confirmation'),
    path('cash_on_delivery/<str:order_number>/', views.Cash_on_delivery, name='cash_on_delivery'),
   
   
    path('order_complete/', views.Order_complete, name='order_complete'),
    path('order_cancel/<int:order_number>/', views.order_cancel, name='order_cancel'),
    path('order_return/<int:order_number>/',views.order_return,name='order_return'),

    path('add_to_wallet/<int:order_number>/',views.add_to_wallet,name='add_to_wallet'),
    path('wallet_data/',views.wallet_data,name='wallet_data'),

    path('generate_invoice_pdf/<int:order_id>/',views.generate_invoice_pdf,name='generate_invoice_pdf'),

   
    
   
   
    

]

   
   

    
    
