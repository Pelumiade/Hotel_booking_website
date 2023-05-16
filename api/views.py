from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics, permissions, serializers
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from rest_framework import status
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from bookings.models import Room, Booking, Complaint
from .serializers import RoomSerializer, ComplaintSerializer, BookingsSerializer, BookingCreateSerializer, BookingSerializer, LoginSerializer, BookSerializer, ComplaintCreateSerializer


class LoginAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class RoomView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ComplaintUpdateView(generics.UpdateAPIView):
    serializer_class = ComplaintSerializer
    queryset = Complaint.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get('pk')
        complaint = get_object_or_404(self.queryset, pk=pk)

        # Only allow updates if status is pending
        if complaint.status != 'pending':
            raise serializers.ValidationError('Complaint cannot be updated as it is no longer pending.')

        return complaint

    def perform_update(self, serializer):
        serializer.save(customer=self.request.user)


class AdminRoomListView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(admin_user=self.request.user, user_id=self.request.user.id)


class AdminRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(admin_user=self.request.user, user_id=self.request.user.id)


class AdminBookingListView(generics.ListAPIView):
    serializer_class = BookingsSerializer
    queryset = Booking.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        booking_id = request.POST.get('booking_id')
        booking = Booking.objects.get(pk=booking_id)
        if 'accept' in request.POST:
            booking.status = 'accepted'
            booking.save()
            # send email notification to customer
            # ...
        elif 'reject' in request.POST:
            booking.status = 'rejected'
            booking.save()
            # send email notification to customer
            # ...
        return self.list(request)
    

class BookingList(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    """
    List all bookings or create a new booking
    """
    def get(self, request, format=None):
        bookings = Booking.objects.all()
        serializer = BookingCreateSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ComplaintList(generics.ListCreateAPIView):
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user)


class ComplaintDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user)


class BookedRoomsList(generics.ListAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        current_bookings = Booking.objects.filter(check_out__gte=timezone.now())
        return current_bookings


class CustomerBookingsAPIView(generics.ListAPIView):
    serializer_class = BookingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Booking.objects.filter(user_id=user_id)    
    

# class AdminComplaintListAPIView(generics.ListCreateAPIView):
#     permission_classes = [permissions.IsAuthenticated,]
#     queryset = Complaint.objects.all()
#     serializer_class = ComplaintSerializer
    
#     def post(self, request, *args, **kwargs):
#         complaint_id = request.data.get('complaint_id')
#         complaint = get_object_or_404(Complaint, pk=complaint_id)
#         if 'mark_as_solved' in request.data:
#             complaint.status = 'solved'
#             complaint.admin_user = request.user
#             complaint.save()
#             messages.success(request, 'Complaint marked as solved!')
#         elif 'mark_as_pending' in request.data:
#             complaint.status = 'pending'
#             complaint.admin_user = request.user
#             complaint.save()
#             messages.success(request, 'Complaint marked as pending!')
#         serializer = ComplaintSerializer(complaint)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
class AdminComplaintListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    def post(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk)

        if 'mark_as_solved' in request.POST:
            complaint.status = 'solved'
            complaint.admin_user = request.user
            complaint.save()
            return Response({'detail': 'Complaint marked as solved!'})
        elif 'mark_as_pending' in request.POST:
            complaint.status = 'pending'
            complaint.admin_user = request.user
            complaint.save()
            return Response({'detail': 'Complaint marked as pending!'})
        else:
            return Response({'detail': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)    

class ComplaintDetailView(APIView):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user)
    
# class RoomListCreateAPIView(generics.ListCreateAPIView):
#     queryset = Room.objects.all()
#     serializer_class = RoomSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user, admin_user=self.request.user)



class RoomListCreateAPIView(generics.CreateAPIView):
    serializer_class = RoomSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, admin_user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, admin_user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomUpdateView(generics.UpdateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user, admin_user=self.request.user)


class RoomDeleteView(generics.DestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        room.delete()
        message = {'detail': 'Room deleted successfully.'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)
    

class BookingAcceptAPIView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def put(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = 'accepted'
        booking.save()
        # send email notification to customer
        send_mail(
            'Booking Accepted',
            'Your booking has been accepted!',
            'fecoyifemi@gmail',  # sender's email
            [booking.customer_email],  # recipient's email
            fail_silently=False,
        )
        return Response({'message': 'Booking accepted.'}, status=status.HTTP_200_OK)
    
class BookingRejectAPIView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def put(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = 'rejected'
        booking.save()

        # send email notification to customer
        send_mail(
            'Booking Rejected',
            'Sorry, your booking has been rejected.',
            'fecoyifemi@gmail.com',  # sender's email
            [booking.customer_email],  # recipient's email
            fail_silently=False,
        )

        return Response({'message': 'Booking rejected.'}, status=status.HTTP_200_OK)
    
class ReleaseRoomAPIView(generics.DestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def destroy(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.room.available = True
        booking.room.save()
        booking.delete()
        return JsonResponse({'message': 'Room released successfully.'}, status=status.HTTP_204_NO_CONTENT)
    
class ComplaintUpdateAPIView(generics.UpdateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAdminUser]
    def put(self, request, *args, **kwargs):
        complaint = self.get_object()
        complaint_id = kwargs.get('pk')
        if 'mark_as_solved' in request.data:
            complaint.status = 'solved'
            complaint.admin_user = request.user
            complaint.save()
            return Response({'message': f'Complaint {complaint_id} marked as solved.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
        
# class BookingCreateAPIView(generics.CreateAPIView):
#     queryset = Booking.objects.all()
#     serializer_class = BookSerializer

#     def post(self, request, *args, **kwargs):
#         room_id = kwargs.get('id')
#         room = get_object_or_404(Room, id=room_id)
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         booking = serializer.save(user=request.user, room=room)
#         booking.save()
#         return Response({'message': 'Your booking has been created.'}, status=status.HTTP_201_CREATED)
class BookingCreateAPIView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response({'message': 'Your booking has been created.'}, status=status.HTTP_201_CREATED)
    
class ComplaintCreateAPIView(generics.CreateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

    def perform_create(self, serializer):
        booking_id = self.kwargs['booking_id']
        serializer.save(user=self.request.user, booking_id=booking_id)