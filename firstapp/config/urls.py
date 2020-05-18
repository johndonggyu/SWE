"""firstapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
#from django.contrib.auth import views as views2

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('main/', views.main, name='main'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('checkuserid/', views.checkuserid, name="checkuserid"),
    path('checkemail/', views.checkemail, name="checkemail"),
    path('findaccount/', views.findaccount, name='findaccount'),
    path('search/<str:kwd>/', views.search, name="search"),
    path('create/', views.create, name='create'),
    path('mypage/', views.mypage, name='mypage'),
    path('mypage/myinfo/', views.myinfo, name='myinfo'),
    path('gsetting/<int:gid>/', views.gsetting, name='gsetting'),
    path('gmain/<int:gid>/', views.gmain, name='gmain'),
    path('withdrawl/', views.withdrawl, name='withdrawl'),
    path('delete3pass/', views.delete3pass, name='delete3pass'),
    path('emailalarm/<str:tf>/', views.emailalarm, name="emailalarm"),
    path('enroll/<int:gid>/', views.enroll, name="enroll"),
    path('leave/<int:groupid>/', views.leave, name="leave"),
    path('leave2/<int:groupid>/', views.leave2, name="leave2"),
    path('gset_enrolled/<int:gid>/', views.gset_enrolled, name='gset_enrolled'),
    path('gset_joined/<int:gid>/', views.gset_joined, name='gset_joined'),
    path('gset_editcontent/<int:gid>/', views.gset_editcontent, name='gset_editcontent'),
    path('gset_noticeadd/<int:gid>/', views.gset_noticeadd, name='gset_noticeadd'),
    path('accept_users/<int:gid>/<str:uid>/', views.accept_users, name='accept_users'),
    path('reject_users/<int:gid>/<str:uid>/', views.reject_users, name='reject_users'),
    path('kick_users/<int:gid>/<str:uid>/', views.kick_users, name='kick_users'),
    path('leave_ownerto_users/<int:gid>/<str:uid>/', views.leave_ownerto_users, name='leave_ownerto_users'),
    path('save_content/<int:gid>/', views.save_content, name='save_content'),
    path('load_content/<int:gid>/', views.load_content, name='load_content'),
    path('chatting/<int:gid>/', views.chatting, name='chatting'),
    path('chat_msg/<int:gid>/', views.chat_msg, name='chat_msg'),
    path('invite/<int:gid>/', views.invite, name='invite'),
    path('present/<int:gid>/', views.present, name='present'),
    path('createvote/<int:gid>/', views.createvote, name='createvote'),
    path('view_items/<int:vid>/', views.view_items, name='view_items'),
    path('voteit/<int:gid>/<int:vid>/', views.voteit, name='voteit'),
]
