from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'book'

urlpatterns = [

    url(r'ajax_calls/search/$', views.autocompleteModel),
    path('',views.BookSearch.as_view(),name='booksearch'),
    path('issued/',views.MyIssuedBook.as_view(),name='myissuedbook'),
    path('issued/approval/',views.ApproveReq.as_view(),name='approval'),
    path('issued/return/',views.ReturnBook.as_view(),name='bookreturn'),
    path('issued/delete/',views.DeleteRequest.as_view(),name='delreq'),
    path('list/',views.AllBookList.as_view(),name='booklist'),
    path('list/request/',views.MyRequestList.as_view(),name='reqlist'),
    path('issued/delreq/',views.DeleteRequestUser.as_view(),name='delrequser'),
    path('issued/list/',views.IssuedBooklist.as_view(),name='issuedlist'),
    path('registration/',views.BookCreate.as_view(),name='bookadd'),
    path('update/<int:pk>/',views.BookUpdate.as_view(),name='bookupdate'),
    path('delete/<int:pk>/',views.BookDelete.as_view(),name='bookdelete'),
]