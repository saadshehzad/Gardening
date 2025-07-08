import uuid
from django.db import models
from plant.models import Product
from users.models import User
from .models import *


class Lawn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name if self.name else "Unnamed Lawn"

class UserLawn(models.Model):
    lawn = models.ForeignKey(Lawn, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Lawn" if self.user else "Unnamed User Lawn"


class LawnProduct(models.Model):
    lawn = models.ForeignKey(Lawn, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.product.name} in {self.lawn.name}" if self.product and self.lawn else "Unnamed Lawn Product"

class RealGardenImages(models.Model):
    description = models.CharField(max_length=255)
    image = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.description if self.description else "Unnamed Image"
    