from allauth.account.utils import send_email_confirmation
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import *


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "_all_" 


class UserRegionProductSerialzier(serializers.Serializer):
    username = serializers.CharField(max_length=30, required=False) 


class CustomRegisterSerializer(RegisterSerializer): 
    email = serializers.EmailField(required=True)

    def custom_signup(self, request, user):
        user.email = self.validated_data.get("email")
        user.save()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value  


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "user", "full_name", "region", "image", "bio", "latitude", "longitude", "share_profile", "share_garden")
        read_only_fields = ("id", "user")
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url 
        return None



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context.get('request')
        data['username'] = self.user.username
        data['uid'] = self.user.id
        data['email'] = self.user.email
        try:
            profile = UserProfile.objects.get(user=self.user)
            data['full_name'] = profile.full_name or ""
            data['region'] = profile.region or ""
            if profile.image and hasattr(profile.image, 'url'):
                data['image'] = request.build_absolute_uri(profile.image.url) if request else profile.image.url
            else:
                data['image'] = None
            data['bio'] = profile.bio or ""
            data['latitude'] = profile.latitude or None
            data['longitude'] = profile.longitude or None
            data['share_profile'] = profile.share_profile
            data['share_garden'] = profile.share_garden
        except UserProfile.DoesNotExist:
            data['full_name'] = ""
            data['region'] = ""
            data['image'] = None
            data['bio'] = ""
            data['latitude'] = None
            data['longitude'] = None
            data['share_profile'] = False
            data['share_garden'] = False

        return data

