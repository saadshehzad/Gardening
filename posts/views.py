from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

from .models import UserPost
from .serializers import *


class PostListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPostSerializer
    queryset = UserPost.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            req_user = request.user
            description = serializer.validated_data.get("description")

            try:
                user = User.objects.get(username=req_user)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )

            try:
                UserPost.objects.create(description=description, user=user)
                return Response(
                    {"message": "Post created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            except:
                return Response({"message": "Error while creating Post."})

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticlesListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = ArticleSerilizer
    queryset = Articles.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            req_user = request.user
            url = serializer.validated_data.get("url")

            try:
                user = User.objects.get(username=req_user)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )

            try:
                Articles.objects.create(url=url)
                return Response(
                    {"message": "article created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            except:
                return Response({"message": "Error while creating article."})

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
