from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class Room(models.Model):
    ROOM_TYPE_CHOICES = (
        ('standard', 'Standard'),
        ('deluxe', 'Deluxe'),
        ('suite', 'Suite'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    admin_user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='room_admin', default=3)
    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='standard')
    room_number = models.PositiveIntegerField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='rooms', blank=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    admin_user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings_admin', default=3)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_choices = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')
    number_of_guests = models.PositiveIntegerField()
    customer_email = models.EmailField(max_length=255)
    customer_name =  models.CharField(max_length=100, default='')

    def __str__(self):
        return f"{self.room.name} - {self.user.email}"


class Complaint(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    admin_user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaint_admin', default=1)
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, null=True)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_choices = [
        ('pending', 'Pending'),
        ('solved', 'Solved'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')

    def __str__(self):
        return self.subject
  
