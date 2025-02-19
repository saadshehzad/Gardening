from rest_framework import serializers

from plant.serializers import ProductSerializer

from .models import *


class LawnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lawn
        fields = "__all__"


class UserLawnSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLawn
        fields = "__all__"


class LawnProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    lawn = LawnSerializer()

    class Meta:
        model = LawnProduct
        fields = "__all__"


class CreateUserLawnProductSerialzier(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    products = serializers.ListField()


class DisplayUserLawnProductSerialzier(serializers.Serializer):
    lawn_id = serializers.CharField(max_length=50, required=False)
