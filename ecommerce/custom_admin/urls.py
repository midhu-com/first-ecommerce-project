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

    path('orders/',views.Orders_view,name='orders'),
    path('order_cancel/<int:order_id>/',views.Order_cancel,name='order_cancel'),
    path('order_return/<int:order_id>/',views.order_returnn,name='order_return'),
    path('invoice/<int:order_id>/',views.Invoice,name='invoice'),

    path('coupons/',views.Coupon_view,name='coupons'),
    path('add_coupon/',views.add_coupon,name='add_coupon'),
    path('edit_coupon/<int:coupon_id>/',views.edit_coupon,name='edit_coupon'),
    path('delete_coupon/<int:coupon_id>/',views.delete_coupon,name='delete_coupon'),

    path('sales_report/',views.sales_report,name='sales_report'),

    path('sales/', views.sales_report, name='sales_report'),
    path('sales/daily/', views.sales_report, {'period': 'daily'}, name='daily_sales_report'),
    path('sales/weekly/', views.sales_report, {'period': 'weekly'}, name='weekly_sales_report'),
    path('sales/monthly/', views.sales_report, {'period': 'monthly'}, name='monthly_sales_report'),
    path('sales/yearly/', views.sales_report, {'period': 'yearly'}, name='yearly_sales_report'),
    path('sales/custom/', views.sales_report, {'period': 'custom'}, name='custom_sales_report'),
    path('sales-report/pdf/<str:period>/<str:start_date>/<str:end_date>/', views.download_sales_report_pdf, name='download_sales_report_pdf'),


    path('sales-report/pdf/<str:period>/', views.download_sales_report_pdf, name='download_sales_report_pdf'),
    # ... other URL patterns

    path('sales-report/excel/<str:period>/', views.sales_report_excel, name='sales_report_excel'),

    


    
    
   



    
    
]