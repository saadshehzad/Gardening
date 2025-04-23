from uuid import UUID
from rest_framework import serializers
from plant.serializers import ProductSerializer
from .models import *


class LawnSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Lawn
        fields = "_all_"


class UserLawnSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLawn
        fields = "_all_"

class LawnProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    lawn = LawnSerializer()

    class Meta:
        model = LawnProduct
        fields = "_all_"


class CreateUserLawnProductSerializer(serializers.Serializer):
    products = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        error_messages={"min_length": "At least one product ID is required."}
    )

    def validate(self, data):
        product_ids = data.get('products', [])
        for product_id in product_ids:
            try:
                UUID(product_id)
            except ValueError:
                raise serializers.ValidationError({"message": "Invalid Product ID"})
        return data


class DisplayUserLawnProductSerializer(serializers.Serializer):
    lawn_id = serializers.CharField(max_length=50, required=False)


class DeleteUserLawnProductSerializer(serializers.Serializer):
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
    

    