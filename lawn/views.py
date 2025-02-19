from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

from .models import Lawn
from .serializers import *


class LawnListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LawnSerializer
    queryset = Lawn.objects.all()


class LawnDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LawnSerializer
    queryset = Lawn.objects.all()
    lookup_field = "id"


class AddProductToUserLawn(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateUserLawnProductSerialzier

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            request_user = serializer.validated_data.get("username")
            # request_userlawn= serializer.validated_data.get("user_lawn_id")
            request_product_ids = serializer.validated_data.get("products")

            try:
                user_ = User.objects.get(username=request_user)
            except:
                return Response(
                    {"message": "User not found."}, status=status.HTTP_404_NOT_FOUND
                )
            try:
                user_lawn = UserLawn.objects.get(user=user_).lawn
            except:
                return Response(
                    {"message": "User lawn not found or does not belong to the user."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            for obj in request_product_ids:
                LawnProduct.objects.create(lawn=user_lawn, product_id=obj)

            return Response(
                {"message": "Products successfully added to the lawn."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DisplayProductToUserLawn(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DisplayUserLawnProductSerialzier

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username_ = request.user
            print(username_)
            lawn_id = UserLawn.objects.get(user__username=username_).lawn.id
            # request_userlawn = serializer.validated_data.get("lawn_id")
            lawn_products = LawnProduct.objects.filter(lawn__id=lawn_id)
            s = LawnProductSerializer(lawn_products, many=True)

            return Response(s.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
