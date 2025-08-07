from django.db import models
from django.conf import settings

class FCMNotification(models.Model):
    TYPE = (("Watering", "Watering"),
            ("Fertilizing", "Fertilizing"),
            ("Pest Check", "Pest Check"),
            ("Trimming", "Trimming"),
    )
    type = models.CharField(max_length=50, choices=TYPE)
    message = models.TextField()
    sent = models.BooleanField(default=False)
    title = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE , null=True, blank=True)
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.title if self.title else 'No Title'}"
