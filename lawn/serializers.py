from uuid import UUID
from rest_framework import serializers
from plant.serializers import ProductSerializer
from .models import *


class LawnSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Lawn
        fields = 'id', 'name', 'created_at'
        def validate_location(self, value):
            if not value:
                raise serializers.ValidationError("Location cannot be empty.")
            return value
        
class UserLawnSerializer(serializers.ModelSerializer):
    lawn = LawnSerializer(read_only=True)
    class Meta:
        model = UserLawn
        fields = ('id', 'user', 'lawn', 'location')

    def validate_location(self, value):
        if not value:
            raise serializers.ValidationError("Location cannot be empty.")
        return value

class LawnProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    lawn = LawnSerializer()

    class Meta:
        model = LawnProduct
        fields = "__all__"

class UserLawnProductSerializer(serializers.Serializer):
    products = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        error_messages={"min_length": "At least one product ID is required."}
    )

    def validate(self, data):
        product_ids = data.get('products', [])
        for product_id in product_ids:
            try:
                uuid.UUID(product_id)
            except ValueError:
                raise serializers.ValidationError({"message": f"Invalid Product ID: {product_id}"})
        return data

class LawnProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawnProduct
        fields = '__all__'

class RealGardenImagesSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    image = serializers.JSONField()
    class Meta:
        model = RealGardenImages
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")
        
