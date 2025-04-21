from rest_framework import serializers

from .models import *
import json

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        def validate_image(self, value):
         if value:
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format for image field")
         return value

   
