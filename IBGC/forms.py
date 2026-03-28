from django import forms
from .models import UploadedImage
from .models import Photo
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['original_image', 'background_image']

class PhotoForm(forms.ModelForm):
    target_size_kb = forms.IntegerField(label="Target Size (KB)")
    class Meta:
        model = Photo
        fields = ['original_image', 'target_size_kb']

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class SigninForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)