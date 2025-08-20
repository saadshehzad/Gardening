from django.conf import settings
from django.db import models
import uuid

class FCMNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TYPE = (
        ("Watering", "Watering"),
        ("Fertilizing", "Fertilizing"),
        ("Pest Check", "Pest Check"),
        ("Trimming", "Trimming"),
        ("Seasonal Plant", "Seasonal Plant"),
        ("Gardeninig Tip", "Gardeninig Tip"),
        ("Seasonal Plant Suggestion", "Seasonal Plant Suggestion"),
        ("Photo Prompt", "Photo Prompt"),
        ("Morning in the Garden", "Morning in the Garden"),
        ("Nature Break", "Nature Break"),
        ("Touch of Green", "Touch of Green"),
        ("Mindful Moment", "Mindful Moment"),
        ("Tiny Care", "Tiny Care"),
        ("Garden Vibes", "Garden Vibes")
    )
    type = models.CharField(max_length=50, choices=TYPE)
    message = models.TextField()
    sent = models.BooleanField(default=False)
    title = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title if self.title else 'No Title'}"
