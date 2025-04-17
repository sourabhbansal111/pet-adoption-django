from django.urls import path
from . import views



urlpatterns = [
    path('carts/', views.cart_detail, name='cart_detail'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('full_remove/<int:product_id>/', views.full_remove, name='full_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('thanks/', views.thank_you, name='thank_you'),
    path('', views.product_list, name='product_list'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

]