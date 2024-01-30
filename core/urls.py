from django.urls import path
from .views import *

urlpatterns = [
    path('products',products,name="products"),
    path('cart', cart, name='cart'),
    path('wishlist', wishlist, name='wishlist'),
    path('ordersapi', ordersapi, name='ordersapi'),
    path('payment', payment, name='payment'),
    path('cfresponse', cfresponse, name='cfresponse'),
    path('returnurl', returnurl, name='returnurl'),
]
