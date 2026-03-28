import os,io
from django.conf import settings
from django.shortcuts import render
from .forms import ImageUploadForm
from rembg import remove
from PIL import Image
from .forms import PhotoForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignupForm, SigninForm


def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.save()
            # Process original image
            original_image = Image.open(uploaded_image.original_image)
            original_image_io = io.BytesIO()
            original_image.save(original_image_io, format='PNG')
            removed_background = remove(original_image_io.getvalue())
            # Ensure 'processed' folder exists
            processed_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
            if not os.path.exists(processed_dir):
                os.makedirs(processed_dir)
            # Save the processed image without background
            processed_image_path = os.path.join(processed_dir, f'{uploaded_image.id}_processed.png')
            with open(processed_image_path, 'wb') as f:
                f.write(removed_background)
            # If background image is provided, overlay it
            if uploaded_image.background_image:
                background_image = Image.open(uploaded_image.background_image)
                foreground_image = Image.open(io.BytesIO(removed_background)).convert("RGBA")
                # Resize background to match foreground size
                background_image = background_image.resize(foreground_image.size)
                # Combine background and foreground
                background_image.paste(foreground_image, (0, 0), foreground_image)
                # Save the new combined image
                combined_image_path = os.path.join(processed_dir, f'{uploaded_image.id}_final.png')
                background_image.save(combined_image_path)
                # Update the model instance
                uploaded_image.processed_image.name = f'processed/{uploaded_image.id}_final.png'
            else:
                # If no background is provided, use the processed image
                uploaded_image.processed_image.name = f'processed/{uploaded_image.id}_processed.png'
            uploaded_image.save()
            return render(request, 'image_success.html', {'image': uploaded_image})
    else:
        form = ImageUploadForm()
    return render(request, 'upload_image.html', {'form': form})

def resize_image(image_path, target_size_kb):
    img = Image.open(image_path)
    quality = 95
    while os.path.getsize(image_path) / 1024 > target_size_kb and quality > 10:
        img.save(image_path, quality=quality)
        quality -= 5

def upload_and_resize(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.save()
            image_path = photo.original_image.path
            target_size_kb = form.cleaned_data['target_size_kb']
            resize_image(image_path, target_size_kb)
            photo.resized_image = photo.original_image
            photo.save()
            return render(request, 'success.html', {'photo': photo})
    else:
        form = PhotoForm()
    return render(request, 'upload.html', {'form': form})
# Home Page with Signup and Signin
def home(request):
    signup_form = SignupForm()
    signin_form = SigninForm()
    if request.method == 'POST':
        if 'signup' in request.POST:  # Signup form submitted
            signup_form = SignupForm(request.POST)
            if signup_form.is_valid():
                signup_form.save()
                messages.success(request, "Account created successfully! Please sign in.")
                return redirect('home')
        elif 'signin' in request.POST:  # Signin form submitted
            signin_form = SigninForm(request.POST)
            if signin_form.is_valid():
                username = signin_form.cleaned_data['username']
                password = signin_form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect('dashboard')
                else:
                    # Show specific error message for failed signin
                    messages.error(request, "Your username or password does not match.")
    return render(request, 'home.html', {
        'signup_form': signup_form,
        'signin_form': signin_form
    })
# Dashboard after successful login
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('home')
    return render(request, 'dashboard.html', {'user': request.user})
# Logout functionality
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')