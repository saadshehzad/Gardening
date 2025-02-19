import uuid

from django.db import models

from plant.models import Product
from users.models import User

from .models import *


class Lawn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class UserLawn(models.Model):
    lawn = models.ForeignKey(
        Lawn,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )


class LawnProduct(models.Model):
    lawn = models.ForeignKey(Lawn, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
