from rest_framework import serializers

from .models import *


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
    image = serializers.ImageField(required=False)

    class Meta:
        model = ReportProblem
        fields = "__all__"
