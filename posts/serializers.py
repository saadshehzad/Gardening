from rest_framework import serializers

from .models import *


class UserPostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    user = serializers.CharField(required=False)

    class Meta:
        model = UserPost
        fields = "__all__"


class ArticleSerilizer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = Articles
        fields = "__all__"
