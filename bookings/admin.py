from django.contrib import admin

# Register your models here.

from .models import Room, Booking, Complaint

# Register your models here.
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Complaint)
