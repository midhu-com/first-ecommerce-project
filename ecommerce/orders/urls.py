from django.urls import path
from .import views
urlpatterns = [
   
    path('place_order/',views.Place_order,name='place_order'),
    
    
]