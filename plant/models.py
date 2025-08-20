import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.models import Region


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    image = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Plant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    image = models.JSONField()
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
    planted_date = models.DateField(null=True, blank=True)
    fertilizer_interval = models.PositiveIntegerField()
    trimming_interval = models.PositiveIntegerField(null=True, blank=True)
    notification_send_date_and_type = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class PlantRegion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True)


class Season(models.Model):
    name = models.CharField(max_length=255, unique=True)
    from_date = models.DateField()
    to_date = models.DateField()

    def __str__(self):
        return self.name


class SeasonalPlant(models.Model):
    name = models.CharField(max_length=255)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name