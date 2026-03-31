import json

from rest_framework import serializers

from .models import *


class CategorySerializer(serializers.ModelSerializer):
    plant_count = serializers.SerializerMethodField()
    plant_images = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "image", "plant_count", "plant_images"]

    def get_plant_count(self, obj):
        return Plant.objects.filter(category=obj).count()

    def get_plant_images(self, obj):
        plants = Plant.objects.filter(category=obj).exclude(image__isnull=True).values_list("image", flat=True)[:10]
        images = []
        for img in plants:
            if isinstance(img, list):
                images.extend(img)
            elif isinstance(img, str):
                try:
                    parsed = json.loads(img)
                    if isinstance(parsed, list):
                        images.extend(parsed)
                    else:
                        images.append(parsed)
                except (json.JSONDecodeError, ValueError):
                    if img.strip():
                        images.append(img)
        return images[:10]


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = "__all__"
