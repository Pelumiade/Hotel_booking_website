from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import Booking, Complaint, Room

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['customer_name', 'customer_email', 'check_in', 'check_out', 'number_of_guests']


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'message']

    
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'price']


class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField()



class CustomerSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(CustomerSignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class BookingStatusForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status']


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'room_type', 'room_number', 'description', 'price', 'image', 'available']

class RoomDeleteForm(forms.Form):
    room_id = forms.IntegerField(widget=forms.HiddenInput)

class ComplaintCreateView(CreateView):
    model = Complaint
    form_class = ComplaintForm
    template_name = 'complaint_create.html'
    success_url = reverse_lazy('complaint_list')


class ComplaintStatusForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status']
        widgets = {
            'status': forms.Select(choices=Complaint.status_choices)
        }
