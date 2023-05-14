from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.contrib.auth.decorators import login_required 
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.template import RequestContext
from django.core.mail import send_mail
from django.views.generic import DetailView, FormView, ListView, CreateView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Room, Booking, Complaint
from accounts.forms import CustomerCreationForm
from .forms import BookingForm,ComplaintForm,BookingStatusForm,RoomForm,ComplaintStatusForm,CustomerSignUpForm
import datetime
User = get_user_model()
# Create your views here.

# HOME PAGE
def home(request):
    rooms = Room.objects.all()
    context = {'rooms': rooms}
    return render(request, 'base.html', context)


# TO SHOW LIST OF ROOMS FOR CUSTOMERS
@login_required
def room_list(request):
    rooms = Room.objects.all()
    bookings = Booking.objects.filter(status='accepted').values_list('room_id', 'check_in', 'check_out')
    booked_rooms = set()
    for booking in bookings:
        room_id, check_in, check_out = booking
        booked_rooms.add(room_id)
        # Remove the room from the set if it's already booked for the requested dates
        if check_in <= datetime.date.today() <= check_out:
            booked_rooms.remove(room_id)
    return render(request, 'room_list.html', {'rooms': rooms, 'booked_rooms': booked_rooms})

# ADMIN: DELETE & CREATE ROOMS
@login_required
def admin_room_list(request):
    rooms = Room.objects.all()

    if request.method == 'POST':
        if 'create' in request.POST:
            form = RoomForm(request.POST, request.FILES)
            if form.is_valid():
                room = form.save(commit=False)
                room.admin_user = request.user
                room.user_id = request.user.id
                room.save()
                messages.success(request, 'Room created successfully.')
            else:
                messages.error(request, 'Error creating room.')
        elif 'update' in request.POST:
            room_id = request.POST.get('room_id')
            room = Room.objects.get(pk=room_id)
            form = RoomForm(request.POST, request.FILES, instance=room)  # pass the room instance to the form
            if form.is_valid():
                form.save()
                messages.success(request, 'Room updated successfully.')
            else:
                messages.error(request, 'Error updating room.')
        elif 'delete' in request.POST:
            room_id = request.POST.get('room_id')
            room = Room.objects.get(pk=room_id)
            room.delete()
            messages.success(request, 'Room deleted successfully.')

        return redirect('bookings:admin_room_list')
    else:
        form = RoomForm()

    return render(request, 'admin_room_list.html', {'rooms': rooms, 'form': form})

#ADMIN: ROOM UPDATE
@login_required
def admin_room_update(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated successfully.')
            return redirect('bookings:admin_room_list')
        else:
            messages.error(request, 'Error updating room.')
    else:
        form = RoomForm(instance=room)

    return render(request, 'admin_room_update.html', {'form': form, 'room': room})

#CUSTOMERS: TO BOOK ROOMS
@login_required
def booking_create(request, id):
    room = get_object_or_404(Room, id=id)
    if request.method == 'POST':
        form = BookingForm(request.POST or None)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room = room
            booking.save()
            messages.success(request, 'Your booking has been created!')
            #return redirect('booking_list')
            return redirect('bookings:home')
            #return redirect('customer:booking_detail', booking_id=booking.id)
    else:
        form = BookingForm()
    return render(request, 'book_room.html', {'room': room, 'form': form})

#CUSTOMER: TO MAKE A COMPLAINT
@login_required
def complaint_create(request, id):
    booking = get_object_or_404(Booking, pk=id)
    if request.method == 'POST':
        form = ComplaintForm(request.POST, pk=booking)  # pass booking object as parameter
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.booking = booking  # set the booking object
            complaint.customer = request.user
            complaint.save()
            messages.success(request, 'Your complaint has been submitted.')
            return redirect('complaint_list')
    else:
        form = ComplaintForm(pk=id)  # pass booking object as parameter
    return render(request, 'complaint_create.html', {'form': form})

#ADMIN:TO ACCEPT OR REJECT BOOKINGS 
@login_required
def admin_booking_list(request):
    bookings = Booking.objects.all()
    if request.method == 'POST':
        form = BookingStatusForm(request.POST)
        booking_id=request.POST.get('booking_id')
        booking = Booking.objects.get(pk=booking_id)
        if 'accept' in request.POST:
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
        elif 'reject' in request.POST:
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
        return redirect('bookings:admin_booking_list')
    else:
        form = BookingStatusForm()

    context = {'bookings': bookings, 'form': form}
    return render(request, 'booking_list.html', context)

#
# @login_required
# def booking_update(request, pk):
#     booking = get_object_or_404(Booking, pk=pk)
#     if request.method == 'POST':
#         form = BookingForm(request.POST, instance=booking)
#         if form.is_valid():
#             booking = form.save(commit=False)
#             booking.customer = request.user
#             booking.save()
#             messages.success(request, 'Booking updated successfully.')
#             return redirect('booking_list')
#     else:
#         form = BookingForm(instance=booking)
    
    
#     return render(request, 'booking_update.html', {'form': form, 'booking': booking})

#CUSTOMER: TO VIEW THE DETAILS OF THEIR BOOKINGS
@login_required
def booking_detail(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booking_detail.html', {'bookings': bookings})

#
# @login_required
# def complaint_list(request, complaint_id):
#     complaint = get_object_or_404(Complaint, pk=complaint_id, customer=request.user)
#     return render(request, 'complaint_list.html', {'complaint': complaint})

#ADMIN: TO SOLVE COMPLAINT
@login_required
def complaint_update(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)

    # Only allow updates if status is pending
    if complaint.status != 'pending':
        messages.error(request, 'Complaint cannot be updated as it is no longer pending.')
        return redirect('complaint_detail', pk=complaint.pk)

    if request.method == 'POST':
        form = ComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.customer = request.user
            complaint.save()
            messages.success(request, 'Complaint updated successfully.')
            return redirect('complaint_list')
    else:
        form = ComplaintForm(instance=complaint)

    return render(request, 'complaint_update.html', {'form': form, 'complaint': complaint})


#CUSTOMER; ROOM DETAIL
class RoomDetailView(DetailView):
    model = Room
    template_name = 'room_detail.html'
    context_object_name = 'room'


    def get_success_url(self):
        return reverse('room_detail', kwargs={'pk': self.object.room.pk})
  

# @login_required
# def admin_home(request):
#     current_bookings = Booking.objects.filter(status='current')
#     past_bookings = Booking.objects.filter(status='past')
#     complaints = Complaint.objects.all()
#     return render(request, 'admin_home.html', {'current_bookings': current_bookings, 'past_bookings': past_bookings, 'complaints': complaints})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('bookings:home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            print(form.errors)

            user = form.save(commit=False)
            user.is_customer = True
            user.save()
            form.save_m2m()
            login(request, user)
            return redirect('bookings:login')
    else:
        form = CustomerSignUpForm()
    return render(request, 'signup.html', {'form': form})


# class ComplaintListView(ListView):
#     model = Complaint
#     template_name = 'complaint_list.html'
#     context_object_name = 'complaints'


# CUSTOMER:TO MAKE A COMPLAINT
class ComplaintCreateView(CreateView):
    model = Complaint
    form_class = ComplaintForm
    template_name = 'complaint_create.html'
    success_url = reverse_lazy('bookings:home')
    

    def form_valid(self, form):
        form.instance.user = self.request.user
        booking_id = self.request.GET.get('booking_id')
        form.instance.booking_id = booking_id
        response = super().form_valid(form)
        messages.success(self.request, 'Your complaint has been submitted successfully!')
        return response

#CUATOMER; complaint detail
class ComplaintDetailView(DetailView):
    model = Complaint
    template_name = 'complaint_detail.html'


@login_required
class ComplaintStatusView(FormView):
    form_class = ComplaintStatusForm
    template_name = 'complaint_status.html'


    def form_valid(self, form):
        complaint = get_object_or_404(Complaint, pk=self.kwargs['pk'])
        complaint.status = form.cleaned_data['status']
        complaint.save()
        return redirect('complaint_detail', pk=complaint.pk)

@login_required
def complaint_detail(request):    
    complaint = Complaint.objects.filter(user=request.user)
    print(complaint)
    return render(request, 'complaint_detail.html', {'complaint': complaint})

@login_required
def admin_complaint_list(request):
    complaints = Complaint.objects.all()
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        complaint = Complaint.objects.get(pk=complaint_id)
        if 'mark_as_solved' in request.POST:
            complaint.status = 'solved'
            complaint.admin_user = request.user
            complaint.save()
            messages.success(request, 'Complaint marked as solved!')
        elif 'mark_as_pending' in request.POST:
            complaint.status = 'pending'
            complaint.admin_user = request.user
            complaint.save()
            messages.success(request, 'Complaint marked as pending!')
        return redirect('bookings:admin_complaint_list')
    context = {'complaints': complaints}
    return render(request, 'complaint_list.html', context)

@login_required
def complaint_edit(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)

    # Check if the complaint belongs to the current user
    if request.user != complaint.user:
        return HttpResponseForbidden()

    # Check if the complaint is already solved
    if complaint.status == 'solved':
        return HttpResponseBadRequest("Cannot edit a solved complaint.")

    if request.method == 'POST':
        form = ComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            complaint = form.save()
            messages.success(request, 'Complaint updated successfully.')
            return redirect('bookings:complaint_detail')
    else:
        form = ComplaintForm(instance=complaint)

    return render(request, 'complaint_update.html', {'form': form, 'complaint': complaint})

@login_required
def customer_info(request):
    bookings = Booking.objects.all()
    return render(request, 'customer_info.html', {'bookings': bookings})

@login_required
def booked_rooms_list(request):
    current_bookings = Booking.objects.filter(check_out__gte=timezone.now())
    past_bookings = Booking.objects.filter(check_out__lt=timezone.now())

    context = {
        'current_bookings': current_bookings,
        'past_bookings': past_bookings,
    }

    return render(request, 'booked_rooms_list.html', context)

@login_required
def release_room(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.room.available = True
    booking.room.save()
    booking.delete()
    return HttpResponseRedirect(reverse('bookings:booked_rooms_list'))

@login_required
def customer_bookings(request, user_id):
    bookings = Booking.objects.filter(user__id=user_id)
    return render(request, 'customer_bookings.html', {'bookings': bookings})

