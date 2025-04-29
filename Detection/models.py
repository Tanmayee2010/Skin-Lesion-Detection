from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    dob = models.DateField(null=True, blank=True)  # Optional
    location = models.CharField(max_length=100, blank=True)  # Optional
    gender = models.CharField(max_length=10, blank=True)  # Optional

    def __str__(self):
        return self.user.username

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
