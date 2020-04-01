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
    path('profile/<int:pk>/',ProfileView.as_view(),name="profile"),
    path('profile/update/<int:pk>/',ProfileUpdate.as_view(),name="update-profile"),
]
