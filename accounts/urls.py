from django.contrib import admin
from django.urls import path

from lms import settings
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('', index, name='index'),
    path('login/',Login.as_view(),name='login'),
    path('registration/',Registration.as_view(),name='registration'),
    path('logout/',Logout,name='logout'),
]
