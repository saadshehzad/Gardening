from uuid import UUID

from rest_framework import serializers

from plant.serializers import PlantSerializer

from .models import *


class LawnSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Lawn
        fields = "id", "name", "created_at"

        def validate_location(self, value):
            if not value:
                raise serializers.ValidationError("Location cannot be empty.")
            return value


class UserLawnSerializer(serializers.ModelSerializer):
    lawn = LawnSerializer(read_only=True)

    class Meta:
        model = UserLawn
        fields = ("id", "user", "lawn", "location")

    def validate_location(self, value):
        if not value:
            raise serializers.ValidationError("Location cannot be empty.")
        return value


class LawnPlantSerializer(serializers.ModelSerializer):
    plant = PlantSerializer()
    lawn = LawnSerializer()

    class Meta:
        model = LawnPlant
        fields = "__all__"


class UserLawnPlantSerializer(serializers.Serializer):
    plants = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        error_messages={"min_length": "At least one plant ID is required."},
    )

    def validate(self, data):
        plant_ids = data.get("plants", [])
        for plant_id in plant_ids:
            try:
                uuid.UUID(plant_id)
            except ValueError:
                raise serializers.ValidationError(
                    {"message": f"Invalid Plant ID: {plant_id}"}
                )
        return data


class LawnPlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawnPlant
        fields = "lawn", "plant"


class RealGardenImagesSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    image = serializers.JSONField()

    class Meta:
        model = RealGardenImages
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")
