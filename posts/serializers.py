import json

from rest_framework import serializers

from lawn.models import UserLawn
from .models import *
from users.models import UserProfile


class PostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source="post.image", required=False)
    description = serializers.CharField(source="post.description", required=False)
    time = serializers.DateTimeField(
        source="post.time",
        format="%Y-%m-%d %H:%M:%S",
        read_only=True,
    )
    user = serializers.CharField(source="user.username", read_only=True)
    profile_picture = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    lawn_id = serializers.SerializerMethodField()

    class Meta:
        model = UserPost
        fields = [
            "id",
            "user",
            "profile_picture",
            "image",
            "description",
            "time",
            "location",
            "bio",
            "post_count",
            "like_count",
            "comment_count",
            "lawn_id",
        ]

    def get_profile_picture(self, obj):
        request = self.context.get("request")

        user_profile = UserProfile.objects.filter(user=obj.user).first()

        if user_profile and user_profile.image:
            if request:
                return request.build_absolute_uri(user_profile.image.url)
            return user_profile.image.url

        return None
    
    def get_location(self, obj):
        return getattr(getattr(obj.user, "userprofile", None), "region", "")

    def get_bio(self, obj):
        return getattr(getattr(obj.user, "userprofile", None), "bio", "")

    def get_post_count(self, obj):
        return UserPost.objects.filter(user=obj.user).count()

    def get_like_count(self, obj):
        return UserPostLike.objects.filter(user_post=obj).count()

    def get_comment_count(self, obj):
        return UserPostComment.objects.filter(user_post=obj).count()

    def get_lawn_id(self, obj):
        user_lawn = (
            UserLawn.objects.filter(user=obj.user)
            .select_related("lawn")
            .first()
        )
        return str(user_lawn.lawn.id) if user_lawn and user_lawn.lawn else None

    def create(self, validated_data):
        post_data = validated_data.pop("post", {})
        request = self.context.get("request")
        user = request.user

        post = Post.objects.create(
            description=post_data.get("description", ""),
            image=post_data.get("image"),
        )

        return UserPost.objects.create(
            user=user,
            post=post,
            **validated_data,
        )

    def update(self, instance, validated_data):
        post_data = validated_data.pop("post", {})
        post = instance.post

        if "description" in post_data:
            post.description = post_data["description"]

        if "image" in post_data:
            post.image = post_data["image"]

        post.save()
        return instance


class ArticleSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S",
        read_only=True,
    )

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
                raise serializers.ValidationError("Invalid JSON format for image field.")
        return value