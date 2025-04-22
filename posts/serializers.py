from rest_framework import serializers
import ast
from .models import *
import json

class UserPostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    user = serializers.CharField(required=False)
    time =serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",read_only=True)

    class Meta:
        model = UserPost
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    created_at=serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",read_only=True)

    class Meta:
        model = Articles
        fields = "__all__"


class ReportProblemSerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = ReportProblem
        fields = "__all__"
   
    def validate_image(self, value):
        if value:
            try:
                image_urls = json.loads(value)  # Convert JSON string back to list
                if not isinstance(image_urls, list):
                    raise serializers.ValidationError("Invalid image URL format.")
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format for image field")
        return value

