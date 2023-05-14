from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse 
from .forms import CustomerCreationForm
from accounts.models import CustomUser
from bookings.forms import CustomerSignUpForm

@login_required(login_url='/login/')
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')
    return render(request, 'accounts/admin_dashboard.html')

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('bookings:login')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error_message = 'Invalid email or password. Please try again.'
            return render(request, 'accounts/login.html', {'error_message': error_message})
    else:
        return render(request, 'accounts/login.html')

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



