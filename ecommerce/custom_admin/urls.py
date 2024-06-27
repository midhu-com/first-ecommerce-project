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
    
    path('add_variation/<int:product_id>',views.add_variation, name='add_variation'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('restore_product/<int:product_id>/', views.restore_product, name='restore_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('product/<int:product_pk>/detailad/', views.product_detailad, name='product_detailad'),
    path('crop-image/<int:variation_id>/', views.crop_image, name='crop_image'),

    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('restore_category/<int:category_id>/', views.restore_category, name='restore_category'),
    path('edit_category<int:category_id>/', views.edit_category, name='edit_category'),
    path('category/<int:category_pk>/detail', views.category_detailad, name='category_detailad'),

    path('orders/',views.Orders_view,name='orders'),
    path('invoice/<int:order_id>/',views.Invoice,name='invoice'),

    path('admin_change_order_status/<int:order_number>/', views.admin_change_order_status, name='admin_change_order_status'),
    path('admin_cancel_order/<int:order_number>/', views.admin_cancel_order, name='admin_cancel_order'),
    path('admin_ship_order/<int:order_number>/', views.admin_ship_order, name='admin_ship_order'),
    path('admin_deliver_order/<int:order_number>/', views.admin_deliver_order, name='admin_deliver_order'),
     path('admin_return_order/<int:order_number>/', views.admin_return_order, name='admin_return_order'),



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



    path('product-offer/create/', views.product_offer_create, name='product_offer_create'),
    path('product-offer/<int:pk>/edit/', views.product_offer_edit, name='product_offer_edit'),
    path('product-offer/<int:pk>/delete/', views.product_offer_delete, name='product_offer_delete'),
    path('product-offers_list/', views.list_product_offers, name='product_offers_list'),
    path('offers/', views.offers, name='offers'),

    # Category Offer URLs
    path('category-offer/create/', views.category_offer_create, name='category_offer_create'),
    path('category-offer/<int:pk>/edit/', views.category_offer_edit, name='category_offer_edit'),
    path('category-offer/<int:pk>/delete/', views.category_offer_delete, name='category_offer_delete'),
    path('category-offers_list/', views.list_category_offers, name='category_offers_list'),


    


    
    
   



    
    
]
