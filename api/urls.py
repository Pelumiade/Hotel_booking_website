from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('rooms/', RoomView.as_view(), name='room_list'),
    path('bookings/<int:pk>/', BookingDetailAPIView.as_view(), name='booking_api'),
    path('bookings/<int:user_id>/', CustomerBookingsAPIView.as_view(), name='customer_bookings'),
    path('complaints/<int:pk>/', ComplaintUpdateView.as_view(), name='complaint_update'),
    path('complaint/', ComplaintList.as_view(), name='complaint-list'),
    path('complaint/<int:pk>/', ComplaintDetail.as_view(), name='complaint-detail'),
    path('complaint_detail/<int:pk>/', ComplaintDetailView.as_view(), name='complaint-detail'),
    path('admin_rooms/', AdminRoomListView.as_view(), name='api_admin_room_list'),
    path('admin_rooms/<int:pk>/', AdminRoomDetailView.as_view(), name='api_admin_room_detail'),
    path('bookings_admin/', AdminBookingListView.as_view(), name='admin_booking_list'),
    path('booking_list/', BookingList.as_view(), name='booking_list'),
    path('booked_rooms/', BookedRoomsList.as_view(), name='booked_rooms_list_api'),
    path('complaints_list/', AdminComplaintListAPIView.as_view(), name='admin_complaint_list'),
    path('rooms_create/', RoomListCreateAPIView.as_view(), name='room-list-create'),
    path('rooms/update/<int:pk>/', RoomUpdateView.as_view(), name='room-update'),
    path('rooms/delete/<int:pk>/', RoomDeleteView.as_view(), name='room-delete'),
    path('bookings/<int:pk>/accept/', BookingAcceptAPIView.as_view(), name='booking_accept'),
    path('bookings/<int:pk>/reject/', BookingRejectAPIView.as_view(), name='booking_reject'),
    path('bookings/<int:pk>/release/', ReleaseRoomAPIView.as_view(), name='api-release-room'),
    path('complaints_solved/<int:pk>/', ComplaintUpdateAPIView.as_view(), name='complaint-update-api'),
    path('bookings/create/<int:id>/', BookingCreateAPIView.as_view(), name='booking_create'),
]



