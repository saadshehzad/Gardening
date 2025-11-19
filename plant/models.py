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
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    llm = models.ForeignKey(LLM, on_delete=models.CASCADE)
    description = models.TextField()
    image = models.TextField()

    variety_info = models.CharField()
    attributes = models.CharField()
    family = models.CharField()
    type = models.CharField()
    native = models.CharField()
    plant_dimension = models.CharField()

    growth_stage = models.CharField(default="Seed")  
    days_to_maturity = models.CharField()
    mature_speed = models.CharField()
    mature_height = models.CharField()
    fruit_size = models.CharField()

    exposure = models.CharField() 
    sunlight_requirement = models.CharField()
    soil_type = models.CharField()
    soil_ph = models.CharField()
    hardiness = models.CharField()  
    temperature_min = models.CharField()
    temperature_max = models.CharField()
    humidity_preference = models.CharField()

    watering_interval = models.CharField() 
    last_watered = models.DateField(null=True, blank=True)
    next_watering_date = models.DateField(null=True, blank=True)

    fertilizer_interval = models.CharField() 
    last_fertilized = models.DateField(null=True, blank=True)
    next_fertilizing_date = models.DateField(null=True, blank=True)

    trimming_interval = models.CharField()
    last_trimmed = models.DateField(null=True, blank=True)
    next_trimming_date = models.DateField(null=True, blank=True)

    planted_date = models.DateField(null=True, blank=True)

    health_status = models.CharField(null=True, blank=True)
    common_pests = models.TextField()
    disease_signs = models.TextField()
    treatment_methods = models.TextField()

    notification_send_date_and_type = models.JSONField(default=dict,null=True, blank=True)

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