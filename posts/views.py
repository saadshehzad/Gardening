from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
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
            image=request.FILES.get('image')
            if not image:
                return Response({"error"})

            try:
                user = User.objects.get(username=req_user)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
            try:
                UserPost.objects.create(description=description, user=user, image=image)
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
    serializer_class = ArticleSerializer
    queryset = Articles.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        image=request.FILES.get("image")

        if serializer.is_valid():
            req_user = request.user
            url = serializer.validated_data.get("url")

            try:
                user = User.objects.get(username=req_user,image=image)
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

class ReportProblemListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportProblemSerializer
    queryset = ReportProblem.objects.all()

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        images = request.FILES.getlist("image")
        image_urls = []
        for image in images:
            try:
                path = default_storage.save(f"images/{image.name}", ContentFile(image.read()))
                relative_url = default_storage.url(path)
                full_url = request.build_absolute_uri(relative_url)
                image_urls.append(full_url)
            except Exception as e:
                return Response({"error": f"Failed to save image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        data["image"] = json.dumps(image_urls) if image_urls else None

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            
            return Response(
                {
                    "message": "Report Problem created successfully",
                    
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)