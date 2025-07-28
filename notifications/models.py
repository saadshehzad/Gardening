from django.db import models


class FCMNotification(models.Model):
    TYPE = (("Watering", "Watering"),)
    type = models.CharField(max_length=50, choices=TYPE)
    message = models.TextField()
    sent = models.BooleanField(default=False)
    title = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title if self.title else 'No Title'}"
