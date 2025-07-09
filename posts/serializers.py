import json

from rest_framework import serializers

from lawn.models import Lawn, UserLawn

from .models import *


class PostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source="post.image", read_only=True)
    description = serializers.CharField(source="post.description", required=False)
    time = serializers.DateTimeField(
        source="post.time", format="%Y-%m-%d %H:%M:%S", read_only=True
    )
    user = serializers.CharField(source="user.username", read_only=True)

    # Additional fields for GET response
    location = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    lawn_id = serializers.SerializerMethodField()

    class Meta:
        model = UserPost
        fields = [
            "id",
            "user",
            "image",
            "description",
            "time",
            "location",
            "bio",
            "posts",
            "likes",
            "comments",
            "lawn_id",
        ]

    def get_location(self, obj):
        return (
            getattr(obj.user.userprofile, "region", "")
            if hasattr(obj.user, "userprofile")
            else ""
        )

    def get_bio(self, obj):
        return (
            getattr(obj.user.userprofile, "bio", "")
            if hasattr(obj.user, "userprofile")
            else ""
        )

    def get_posts(self, obj):
        return UserPost.objects.filter(user=obj.user).count()

    def get_likes(self, obj):
        return UserPostLike.objects.filter(user_post=obj).count()

    def get_comments(self, obj):
        return UserPostComment.objects.filter(user_post=obj).count()

    def get_lawn_id(self, obj):
        try:
            user_lawn = UserLawn.objects.get(user=obj.user)
            return str(user_lawn.lawn.id)
        except UserLawn.DoesNotExist:
            return None


class ArticleSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Articles
        fields = "__all__"


class ReportProblemSerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = ReportProblem
        fields = ["image", "description"]

    def validate_image(self, value):
        if value:
            try:
                image_urls = json.loads(value)
                if not isinstance(image_urls, list):
                    raise serializers.ValidationError("Invalid image URL format.")
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format for image field")
        return value
