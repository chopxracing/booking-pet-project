"""
URL configuration for DjangoBooking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from . import views
from .views import SearchHotel, HotelDetailView, HotelRoomsDetailView, RoomDetailView, BookRoomDetailView, \
    uploadroomphoto

urlpatterns = [
    path('', views.home, name='home'),
    path('hotels/', SearchHotel.as_view(), name='hotels'),
    path('help/', views.help, name='help'),
    path('about/', views.about, name='about'),
    path('login/', views.loginform, name='login'),
    path('register/', views.register, name='register'),
    path('createuser/', views.createuser, name='createuser'),
    path('logincheck/', views.logincheck, name='logincheck'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),

    path('hotels/<int:pk>/', HotelDetailView.as_view(), name='hotel'),

    path('client/', views.clientprofile, name='client'),

    path('createhotel/', views.createhotel, name='client_add_hotel'),

    path('hotel/<int:pk>/rooms/', HotelRoomsDetailView.as_view(), name='rooms'),

    path('rooms/room/<int:pk>/', RoomDetailView.as_view(), name='room_detail'),

    path('client/addphoto', views.uploadhotelphoto, name='client_add_photo'),

    path('bookroom/<int:pk>/', BookRoomDetailView.as_view(), name='bookroom_detail'),

    path('room/rooms/<int:pk>/addphoto', views.uploadroomphoto, name='room_add_photo'),

    path('rooms/createroom', views.createroom, name='client_add_room'),
]
