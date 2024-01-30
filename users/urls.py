from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
   path('reg', register,name='register'),
   path('login',login_view,name='login'),
   path('reset',reset_password,name='reset')
]