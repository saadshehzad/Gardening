import json

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from rest_framework import generics, pagination, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lawn.serializers import *

from .models import Lawn, LawnPlant, Plant, RealGardenImages, UserLawn


class LawnListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LawnSerializer
    queryset = Lawn.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if UserLawn.objects.filter(user=user).exists():
            raise ValidationError("You can only create one lawn.")
        lawn = serializer.save()

        location = self.request.data.get("location")
        if not location:
            raise ValidationError("Location is required.")
        UserLawn.objects.create(user=user, lawn=lawn, location=location)


class UserLawnRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLawnSerializer

    def get_object(self):
        user = self.request.user
        return get_object_or_404(UserLawn, user=user)

    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        return Response({"detail": "Location updated successfully."})



class LawnDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LawnSerializer
    queryset = Lawn.objects.all()
    lookup_field = "id"


class UserLawnPlantAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLawnPlantSerializer

    def get(self, request, *args, **kwargs):
        """Retrieve all plants in the user's lawn."""
        user = request.user
        try:
            user_lawn = UserLawn.objects.get(user=user)
            lawn_plants = LawnPlant.objects.filter(lawn=user_lawn.lawn)
            serializer = LawnPlantSerializer(lawn_plants, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserLawn.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Add plants to the user's lawn."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            plant_ids = serializer.validated_data["plants"]
            user = request.user
            user_lawn, created = UserLawn.objects.get_or_create(
                user=user,
                defaults={"lawn": Lawn.objects.create(name=f"{user.username}'s Lawn")},
            )
            lawn = user_lawn.lawn

            lawn_plants = []
            for plant_id in plant_ids:
                try:
                    plant = Plant.objects.get(id=plant_id)
                    if LawnPlant.objects.filter(lawn=lawn, plant=plant).exists():
                        return Response(
                            {
                                "message": f"This plant is already assigned to your lawn."
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    lawn_plant = LawnPlant.objects.create(
                        lawn=lawn, plant=plant
                    )
                    lawn_plants.append(lawn_plant)
                except Plant.DoesNotExist:
                    return Response(
                        {"message": f"Plant does not exist."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            response_serializer = LawnPlantSerializer(lawn_plants, many=True)
            return Response(
                {
                    "message": "Plants successfully added to the lawn.",
                    "data": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """Remove plants from the user's lawn."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            plant_ids = serializer.validated_data["plants"]
            user = request.user

            try:
                user_lawn = UserLawn.objects.get(user=user)
                lawn = user_lawn.lawn
            except UserLawn.DoesNotExist:
                return Response(
                    {"message": "You do not have a lawn."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            deleted_plants = []
            for plant_id in plant_ids:
                try:
                    plant = Plant.objects.get(id=plant_id)
                    lawn_plant = LawnPlant.objects.filter(
                        lawn=lawn, plant=plant
                    ).first()
                    if not lawn_plant:
                        return Response(
                            {
                                "message": f"This plant is not assigned to your lawn."
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    lawn_plant.delete()
                    deleted_plants.append(lawn_plant)
                except Plant.DoesNotExist:
                    return Response(
                        {"message": f"Plant does not exist."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            response_serializer = LawnPlantSerializer(deleted_plants, many=True)
            return Response(
                {
                    "message": "Plants successfully removed from the lawn.",
                    "data": response_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RealGardenImagesAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RealGardenImagesSerializer
    queryset = RealGardenImages.objects.all()
    pagination_class = pagination.PageNumberPagination

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        images = request.FILES.getlist("image")
        image_urls = []
        for image in images:
            try:
                path = default_storage.save(
                    f"images/{image.name}", ContentFile(image.read())
                )
                relative_url = default_storage.url(path)
                full_url = request.build_absolute_uri(relative_url)
                image_urls.append(full_url)
            except Exception as e:
                return Response(
                    {"error": f"Failed to save image: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        data["image"] = json.dumps(image_urls) if image_urls else None
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Plant added successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RealGardenImagesDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RealGardenImagesSerializer
    queryset = RealGardenImages.objects.all()
    lookup_field = "pk"

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        images = request.FILES.getlist("image")
        if images:
            if instance.image:
                old_image_urls = (
                    json.loads(instance.image)
                    if isinstance(instance.image, str)
                    else instance.image
                )
                for url in old_image_urls:
                    try:
                        path = url.split("/media/")[-1] if "/media/" in url else url
                        if default_storage.exists(path):
                            default_storage.delete(path)
                    except Exception as e:
                        pass

            image_urls = []
            for image in images:
                try:
                    path = default_storage.save(f"images/{image.name}", image)
                    relative_url = default_storage.url(path)
                    full_url = request.build_absolute_uri(relative_url)
                    image_urls.append(full_url)
                except Exception as e:
                    return Response(
                        {"error": f"Failed to save image: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            data["image"] = json.dumps(image_urls)

        serializer = self.get_serializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Post updated successfully",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.image:
            image_urls = (
                json.loads(instance.image)
                if isinstance(instance.image, str)
                else instance.image
            )
            for url in image_urls:
                try:
                    path = url.split("/media/")[-1] if "/media/" in url else url
                    if default_storage.exists(path):
                        default_storage.delete(path)
                except Exception as e:
                    pass

        instance.delete()
        return Response(
            {"detail": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )