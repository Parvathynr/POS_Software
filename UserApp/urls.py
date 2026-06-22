from django.urls import path

from UserApp import views


urlpatterns = [
    path('', views.product_list, name='products'),
    path('cart/', views.view_cart, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_cart'),
    path('update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('sales/', views.sales_history, name='sales'),
]