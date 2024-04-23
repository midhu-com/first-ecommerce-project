from django.urls import path
from .import views
urlpatterns = [
   
    path('payments/', views.Payments, name='payments'),
    path('place_order/', views.Place_order, name='place_order'),
    path('order_confirmation/<str:order_number>/', views.Order_Confirmation, name='order_confirmation'),
    path('cash_on_delivery/<str:order_number>/', views.Cash_on_delivery, name='cash_on_delivery'),
   
    #path('add_address/', views.Add_address, name='add_address'),
    #path('edit/<int:address_id>/', views.Edit_address, name='edit_address'),
    #path('delete/<int:address_id>/', views.Delete_address, name='delete_address'),

    path('cancel_order/<int:order_number>/', views.cancel_orderr, name='cancel_order'),

]

   
   

    
    
