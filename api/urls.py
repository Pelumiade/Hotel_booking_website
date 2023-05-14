from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('rooms/', RoomView.as_view(), name='room_list'),
    #path('bookings/<int:pk>/', BookingDetailAPIView.as_view(), name='booking_api'),
    path('bookings/<int:user_id>/', CustomerBookingsAPIView.as_view(), name='customer_bookings'),
    path('complaints/<int:pk>/', ComplaintUpdateView.as_view(), name='complaint_update'),
    path('complaint/', ComplaintList.as_view(), name='complaint-list'),
    path('complaint/<int:pk>/', ComplaintDetail.as_view(), name='complaint-detail'),
    path('admin_rooms/', AdminRoomListView.as_view(), name='api_admin_room_list'),
    path('admin_rooms/<int:pk>/', AdminRoomDetailView.as_view(), name='api_admin_room_detail'),
    path('bookings_admin/', AdminBookingListView.as_view(), name='admin_booking_list'),
    path('booking_list/', BookingList.as_view(), name='booking_list'),
    path('booked_rooms/', BookedRoomsList.as_view(), name='booked_rooms_list_api'),
    path('complaints_list/', AdminComplaintListAPIView.as_view(), name='admin_complaint_list'),
]

