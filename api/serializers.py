from rest_framework import generics, serializers
from bookings.models import Room, Booking, Complaint
from django.contrib.auth import authenticate

from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                return user
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class RoomList(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


# class BookingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Booking
#         fields = '__all__'



class BookingSerializer(serializers.ModelSerializer):
    room = RoomSerializer()

    class Meta:
        model = Booking
        fields = ['id', 'room', 'check_in', 'check_out', 'status', 'number_of_guests', 'customer_email', 'customer_name']


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['id', 'user', 'admin_user', 'booking', 'subject', 'message', 'status', 'created_at', 'updated_at']


class BookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'user', 'room', 'cheack_in', 'check_out', 'created_at']


# class BookSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Booking
#         fields = ['id', 'user', 'room', 'check_in', 'check_out', 'number_of_guests', 'customer_email', 'customer_name']
#         read_only_fields = ['id', 'user', 'room']

#     def create(self, validated_data):
#         user = self.context['request'].user
#         room = self.context['room']
#         booking = Booking.objects.create(
#             user=user,
#             room=room,
#             **validated_data
#         )
#         return booking
class BookSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(write_only=True)  # Add write-only field for room ID

    class Meta:
        model = Booking
        fields = ['id', 'user', 'room_id', 'check_in', 'check_out', 'number_of_guests', 'customer_email', 'customer_name']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        room_id = validated_data.pop('room_id')  # Retrieve room ID from validated data
        room = Room.objects.get(id=room_id)  # Retrieve the room using the ID
        booking = Booking.objects.create(
            user=user,
            room=room,
            **validated_data
        )
        return booking
    
class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['subject', 'message']