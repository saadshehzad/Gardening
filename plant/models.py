import uuid
from django.db import models
from users.models import Region


class LLM(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    image = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Season(models.Model):
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"

    SEASON_CHOICES = (
        (WINTER, "Winter"),
        (SPRING, "Spring"),
        (SUMMER, "Summer"),
        (FALL, "Fall"),
    )

    name = models.CharField(max_length=20, choices=SEASON_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Plant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    llm = models.ForeignKey(LLM, on_delete=models.CASCADE)
    description = models.TextField()
    image = models.JSONField(default=list, blank=True , null=True)

    variety_info = models.CharField(max_length=255)
    attributes = models.CharField(max_length=255)
    family = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    native = models.CharField(max_length=255)
    plant_dimension = models.CharField(max_length=255)

    growth_stage = models.CharField(max_length=255, default="Seed")
    days_to_maturity = models.CharField(max_length=255)
    mature_speed = models.CharField(max_length=255)
    mature_height = models.CharField(max_length=255)
    fruit_size = models.CharField(max_length=255)

    exposure = models.CharField(max_length=255)
    sunlight_requirement = models.CharField(max_length=255)
    soil_type = models.CharField(max_length=255)
    soil_ph = models.CharField(max_length=255)
    hardiness = models.CharField(max_length=255)
    temperature_min = models.CharField(max_length=255)
    temperature_max = models.CharField(max_length=255)
    humidity_preference = models.CharField(max_length=255)

    watering_interval = models.CharField(max_length=255)
    last_watered = models.DateField(null=True, blank=True)
    next_watering_date = models.DateField(null=True, blank=True)

    fertilizer_interval = models.CharField(max_length=255)
    last_fertilized = models.DateField(null=True, blank=True)
    next_fertilizing_date = models.DateField(null=True, blank=True)

    trimming_interval = models.CharField(max_length=255)
    last_trimmed = models.DateField(null=True, blank=True)
    next_trimming_date = models.DateField(null=True, blank=True)

    planted_date = models.DateField(null=True, blank=True)

    health_status = models.CharField(max_length=255, null=True, blank=True)
    common_pests = models.TextField()
    disease_signs = models.TextField()
    treatment_methods = models.TextField()

    notification_send_date_and_type = models.JSONField(default=dict, null=True, blank=True)

    seasons = models.ManyToManyField("Season", related_name="plants", blank=True)

    def __str__(self):
        return self.name


class PlantRegion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("plant", "region")
