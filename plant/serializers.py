import json

from rest_framework import serializers

from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.JSONField()

    class Meta:
        model = Product
        fields = "__all__"

    # def validate_image(self, value):
    #     if value:
    #         try:
    #             image_urls = json.loads(value)
    #             if not isinstance(image_urls, list):
    #                 raise serializers.ValidationError("Invalid image URL format.")
    #         except json.JSONDecodeError:
    #             raise serializers.ValidationError("Invalid JSON format for image field")
    #     return value
