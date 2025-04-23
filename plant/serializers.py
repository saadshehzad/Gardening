from rest_framework import serializers
from .models import *
import json

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False, allow_null=True)
    class Meta:
        model = Product
        fields = "__all__"
 
    def validate_image(self, value):
        if value:
            try:
                image_urls = json.loads(value)
                if not isinstance(image_urls, list):
                    raise serializers.ValidationError("Image field must be a list.")
                if not all(isinstance(i, str) for i in image_urls):
                    raise serializers.ValidationError("All items in the image list must be strings.")
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format for image field")
        return value
    


    
   
