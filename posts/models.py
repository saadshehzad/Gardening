import uuid

from django.db import models

from users.models import User


class UserPost(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    image = models.ImageField(upload_to="images/", null=True)
    description = models.TextField(max_length=100, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class Articles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to="images/")
    url = models.CharField(max_length=1000)
