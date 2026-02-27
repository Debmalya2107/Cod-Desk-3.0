# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentSignUpForm, ProfileUpdateForm

# 1. REGISTER VIEW
def register_view(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log them in immediately after signing up
            messages.success(request, "Account created successfully! Welcome to StudentCollab.")
            return redirect('home')
    else:
        form = StudentSignUpForm()
    return render(request, 'users/register.html', {'form': form})

# 2. LOGIN VIEW
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# 3. LOGOUT VIEW
def logout_view(request):
    logout(request)
    messages.info(request, "You have been securely logged out.")
    return redirect('home')

# 4. PROFILE SETTINGS VIEW (NEW)
@login_required
def profile_settings(request):
    if request.method == 'POST':
        # request.FILES is required to handle the profile picture upload
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been successfully updated!")
            return redirect('profile_settings')
    else:
        # Pre-fill the form with the user's current data
        form = ProfileUpdateForm(instance=request.user)
        
    return render(request, 'users/profile.html', {'form': form})