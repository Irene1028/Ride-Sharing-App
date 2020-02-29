from django.urls import path, include
from django.conf.urls import url
from django.views.generic import RedirectView

from . import views
# from django.views.generic import RedirectView
# from django.contrib.auth.views import PasswordChangeView


urlpatterns = [
    path('', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('user_register/', views.user_register, name='user_register'),
    path('logout/', views.logout, name='logout'),
    path('driver_register/', views.driver_register, name='driver_register'),

    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/edit_vehicle/', views.edit_vehicle, name='edit_vehicle'),
    path('profile/change_password/', views.change_password, name='change_password'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('home/owner_request_ride/', views.request_ride, name='request_ride'),
    path('ride/my_user_requests/', views.MyRequestListView.as_view(), name='my_user_request'),
    path('ride/ride_details/<uuid:pk>', views.MyRideDetailView.ride_detail_view, name='ride_detail_view'),
    path('ride/ride_edit/<uuid:pk>', views.OwnRideEditView.own_ride_edit, name='own_ride_edit'),
    path('ride/ride_cancelled/<uuid:pk>', views.cancel_ride, name='cancel_ride'),


    path('ride/sharer_search_ride/', views.share_search_ride, name='sharer_search_ride'),
    path('ride/sharer_ride_details/<uuid:pk>', views.SharerRideDetailView.sharer_ride_detail_view,
         name='sharer_ride_detail_view'),
    path('ride/sharer_search_ride/joinable_list/', views.show_share_search_result, name='show_share_search_result'),
    path('ride/sharer_search_ride/joined_detail_view/<uuid:pk>/<int:share_passengers>', views.sharer_join_the_ride,
         name='sharer_join_and_show_the_ride'),

    path('ride/sharer_edit/<uuid:pk>', views.sharer_ride_edit, name='sharer_ride_edit'),
    path('ride/sharer_cancel/<uuid:pk>', views.sharer_ride_cancel, name='sharer_ride_cancel'),

    path('ride/driver_search_ride/', views.driver_search_and_result, name='driver_search_ride'),
    path('ride/driver_search_ride/detail_view/<uuid:pk>', views.driver_join_ride, name='driver_join_and_show_the_ride'),
    path('ride/ride_details/complete/<uuid:pk>', views.complete_ride, name='complete_ride'),
    path('ride/driver_ride_details/<uuid:pk>', views.DriverRideDetailView.driver_ride_detail_view,
         name='driver_ride_detail_view'),


]
