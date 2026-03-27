import json

from rest_framework import serializers

from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = "__all__"
