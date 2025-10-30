import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.models import Region

class LLM(models.Model):
    name = models.CharField(max_length=255,unique=True)

    def __str__(self):
        return self.name
    

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
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    llm = models.ForeignKey(LLM, on_delete=models.CASCADE)
    description = models.TextField(max_length=255)
    image = models.JSONField()

    variety_info = models.CharField(max_length=200)
    attributes = models.CharField(max_length=200)
    family = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    native = models.CharField(max_length=50)
    plant_dimension = models.CharField(max_length=50)

    growth_stage = models.CharField(max_length=50, default="Seed")  
    days_to_maturity = models.CharField(max_length=20)
    mature_speed = models.CharField(max_length=20)
    mature_height = models.CharField(max_length=20)
    fruit_size = models.CharField(max_length=20)

    exposure = models.CharField(max_length=100) 
    sunlight_requirement = models.CharField(max_length=50, blank=True, null=True)
    soil_type = models.CharField(max_length=100, blank=True, null=True)
    soil_ph = models.CharField(max_length=20, blank=True, null=True)
    hardiness = models.CharField(max_length=200)  
    temperature_min = models.CharField(max_length=20, blank=True, null=True)
    temperature_max = models.CharField(max_length=20, blank=True, null=True)
    humidity_preference = models.CharField(max_length=50, blank=True, null=True)

    watering_interval = models.CharField(max_length=20, null=True) 
    last_watered = models.DateField(null=True, blank=True)
    next_watering_date = models.DateField(null=True, blank=True)

    fertilizer_interval = models.CharField(max_length=20, null=True) 
    last_fertilized = models.DateField(null=True, blank=True)
    next_fertilizing_date = models.DateField(null=True, blank=True)

    trimming_interval = models.CharField(max_length=20, null=True)
    last_trimmed = models.DateField(null=True, blank=True)
    next_trimming_date = models.DateField(null=True, blank=True)

    planted_date = models.DateField(null=True, blank=True)

    health_status = models.CharField(max_length=50, default="Healthy")
    common_pests = models.TextField(blank=True, null=True)
    disease_signs = models.TextField(blank=True, null=True)
    treatment_methods = models.TextField(blank=True, null=True)

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