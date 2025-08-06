import uuid

from allauth.account.utils import send_email_confirmation
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from lawn.models import Lawn, UserLawn

from .models import *

User = get_user_model()


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "_all_"


class UserRegionPlantSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30, required=False)


class CustomRegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    location = serializers.JSONField(required=True)

    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2", "location")

    def get_location(self, obj):
        request = self.context.get("request")
        if request:
            return request.data.get("location")
        return None

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        validate_password(data["password1"])
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password1"],
            verified=False,
        )
        return user

    def save(self, request):
        user = self.create(self.validated_data)
        location = self.get_location(user)

        fcm_token = request.data.get("fcm_token")
        if fcm_token:
            UserFCMToken.objects.create(user=user, fcm_token=fcm_token)
        user.email = self.validated_data.get("email")
        user.save()

        lawn = Lawn.objects.create(name=f"{user.username}'s Lawn")
        UserLawn.objects.create(user=user, lawn=lawn, location=location)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context.get("request")
        self.user = authenticate(
            request, username=attrs.get("username"), password=attrs.get("password")
        )

        if self.user:
            data["username"] = self.user.username
            data["uid"] = self.user.id
            data["email"] = self.user.email

            try:
                profile = UserProfile.objects.get(user=self.user)
                data["full_name"] = profile.full_name or ""
                data["region"] = profile.region or ""
                if profile.image and hasattr(profile.image, "url"):
                    data["image"] = (
                        request.build_absolute_uri(profile.image.url)
                        if request
                        else profile.image.url
                    )
                else:
                    data["image"] = None
                data["bio"] = profile.bio or ""
                data["share_profile"] = profile.share_profile
                data["share_garden"] = profile.share_garden
            except UserProfile.DoesNotExist:
                data["full_name"] = ""
                data["region"] = ""
                data["image"] = None
                data["bio"] = ""
                data["share_profile"] = False
                data["share_garden"] = False

        return data


class PasswordChangeSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password1"] != data["new_password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(data["new_password1"], self.context["request"].user)
        return data


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user",
            "full_name",
            "region",
            "image",
            "bio",
            "share_profile",
            "share_garden",
        )
        read_only_fields = ("id", "user")

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
