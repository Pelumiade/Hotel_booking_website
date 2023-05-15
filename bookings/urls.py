from django.urls import path
from .import views


app_name = 'bookings'
         
# ]
urlpatterns = [
    
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),

    # Admin URLs
    path('rooms/', views.room_list, name='room_list'),
    path('admin_bookings/', views.admin_booking_list, name='admin_booking_list'),
    #path('bookings/<int:pk>/update/', views.booking_update, name='booking_update'),
    path('admin_rooms/<int:pk>/', views.RoomDetailView.as_view(), name='admin_room_detail'),
    path('admin_room_list/', views.admin_room_list, name='admin_room_list'),
    path('release/<int:booking_id>/', views.release_room, name='release_room'),
    path('customer_info/', views.customer_info, name='customer_info'),
    path('customer_bookings/<int:user_id>/', views.customer_bookings, name='customer_bookings'),
    path('booked_rooms_list/', views.booked_rooms_list, name='booked_rooms_list'),
    path('admin_complaints/', views.admin_complaint_list, name='admin_complaint_list'),
    path('admin_room_update/<int:room_id>/', views.admin_room_update, name='admin_room_update'),
    path('admin_room_create/', views.admin_room_create, name='admin_room_create'),

    # Customer URLs
    path('bookings/<int:id>/create/', views.booking_create, name='booking_create'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('booking/', views.booking_detail, name='booking_detail'), 
    path('complaints/<int:pk>/update/', views.complaint_update, name='complaint_update'),
    path('complaints/', views.complaint_detail, name='complaint_detail'),
    path('complaint_edit/<int:complaint_id>/', views.complaint_edit, name='complaint_edit'),
    path('complaints/create/', views.ComplaintCreateView.as_view(), name='complaint_create'),
    

]
