import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.models import Region


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=20)
    image = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=15)
    image = models.CharField(max_length=255)
    days_to_maturity = models.CharField(max_length=20)
    mature_speed = models.CharField(max_length=20)
    mature_height = models.CharField(max_length=20)
    fruit_size = models.CharField(max_length=20)
    family = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    native = models.CharField(max_length=50)
    hardiness = models.CharField(max_length=200)
    exposure = models.CharField(max_length=100)
    plant_dimension = models.CharField(max_length=50)
    variety_info = models.CharField(max_length=200)
    attributes = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProductRegion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True)
