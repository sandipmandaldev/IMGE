from django.db import models

class UploadedImage(models.Model):
    original_image = models.ImageField(upload_to='originals/')
    background_image = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    processed_image = models.ImageField(upload_to='processed/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Photo(models.Model):
    original_image = models.ImageField(upload_to='original_images/')
    resized_image = models.ImageField(upload_to='resized_images/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)