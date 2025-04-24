from rest_framework import serializers
import json
from .models import *

class PostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='post.image', read_only=True)
    description = serializers.CharField(source='post.description', required=False)
    time = serializers.DateTimeField(source='post.time', format="%Y-%m-%d %H:%M:%S", read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserPost
        fields = ['id', 'user', 'image', 'description', 'time']

class ArticleSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Articles
        fields = '__all__'

class ReportProblemSerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = ReportProblem
        fields = ['image', 'description']

    def validate_image(self, value):
        if value:
            try:
                image_urls = json.loads(value)
                if not isinstance(image_urls, list):
                    raise serializers.ValidationError("Invalid image URL format.")
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format for image field")
        return value