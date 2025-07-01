import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True),
    country = models.CharField(max_length=20, null=True, blank=True)
    verified = models.CharField(default=False,blank=True,max_length=20)    


class Region(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class UserRegion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    share_profile = models.BooleanField(default=True, blank=True)
    share_garden = models.BooleanField(default=True, blank=True)
    
    

    def __str__(self):
        return self.user.username
