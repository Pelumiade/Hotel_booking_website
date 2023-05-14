from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, permissions, serializers
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from bookings.models import Room, Booking, Complaint
from .serializers import RoomSerializer, ComplaintSerializer, BookingsSerializer, BookingCreateSerializer, BookingSerializer, LoginSerializer


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

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
    

class AdminComplaintListAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    
    def post(self, request, *args, **kwargs):
        complaint_id = request.data.get('complaint_id')
        complaint = get_object_or_404(Complaint, pk=complaint_id)
        if 'mark_as_solved' in request.data:
            complaint.status = 'solved'
            complaint.admin_user = request.user
            complaint.save()
            messages.success(request, 'Complaint marked as solved!')
        elif 'mark_as_pending' in request.data:
            complaint.status = 'pending'
            complaint.admin_user = request.user
            complaint.save()
            messages.success(request, 'Complaint marked as pending!')
        serializer = ComplaintSerializer(complaint)
        return Response(serializer.data, status=status.HTTP_200_OK)
