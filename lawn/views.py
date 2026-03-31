import json

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from rest_framework import generics, pagination, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from plant.models import Plant
from plant.views import parse_image_field
from .models import Lawn, LawnPlant, RealGardenImages, UserLawn
from .serializers import (
    LawnSerializer,
    UserLawnSerializer,
    LawnPlantSerializer,
    UserLawnPlantSerializer,
    RealGardenImagesSerializer,
)


class LawnListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LawnSerializer

    def get_queryset(self):
        return Lawn.objects.all().order_by("-created_at")

    def perform_create(self, serializer):
        user = self.request.user

        if UserLawn.objects.filter(user=user).exists():
            raise ValidationError({"message": "You can only create one lawn."})

        location = self.request.data.get("location")
        if not location:
            raise ValidationError({"location": "Location is required."})

        lawn = serializer.save()
        UserLawn.objects.create(user=user, lawn=lawn, location=location)


class MyLawnRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLawnSerializer

    def get_object(self):
        return get_object_or_404(
            UserLawn.objects.select_related("user", "lawn"),
            user=self.request.user,
        )

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Lawn updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UserLawnDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLawnSerializer
    lookup_field = "user_id"
    lookup_url_kwarg = "user_id"

    def get_queryset(self):
        return UserLawn.objects.select_related("user", "lawn")


class LawnDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LawnSerializer
    queryset = Lawn.objects.all()
    lookup_field = "id"


class MyLawnPlantAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLawnPlantSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        user_lawn = UserLawn.objects.filter(user=user).select_related("lawn").first()

        if not user_lawn:
            return Response([], status=status.HTTP_200_OK)

        lawn_plants = LawnPlant.objects.filter(
            lawn=user_lawn.lawn,
            user=user,
        ).select_related("lawn", "plant", "user")

        serializer = LawnPlantSerializer(lawn_plants, many=True)
        data = serializer.data
        for item in data:
            if "plant" in item and item["plant"]:
                item["plant"]["image"] = parse_image_field(item["plant"].get("image"))
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        plant_ids = serializer.validated_data["plants"]
        user = request.user

        user_lawn = UserLawn.objects.filter(user=user).select_related("lawn").first()
        if not user_lawn:
            return Response(
                {"message": "You do not have a lawn. Create a lawn first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lawn = user_lawn.lawn
        lawn_plants = []

        for plant_id in plant_ids:
            plant = Plant.objects.filter(id=plant_id).first()
            if not plant:
                return Response(
                    {"message": f"Plant does not exist: {plant_id}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if LawnPlant.objects.filter(lawn=lawn, plant=plant, user=user).exists():
                return Response(
                    {"message": f"This plant is already assigned to your lawn."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            lawn_plant = LawnPlant.objects.create(lawn=lawn, plant=plant, user=user)
            lawn_plants.append(lawn_plant)

        response_serializer = LawnPlantSerializer(lawn_plants, many=True)
        response_data = response_serializer.data
        for item in response_data:
            if "plant" in item and item["plant"]:
                item["plant"]["image"] = parse_image_field(item["plant"].get("image"))
        return Response(
            {
                "message": "Plants successfully added to the lawn.",
                "data": response_data,
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        plant_ids = serializer.validated_data["plants"]
        user = request.user

        user_lawn = UserLawn.objects.filter(user=user).select_related("lawn").first()
        if not user_lawn:
            return Response(
                {"message": "You do not have a lawn."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lawn = user_lawn.lawn
        deleted_plants = []

        for plant_id in plant_ids:
            plant = Plant.objects.filter(id=plant_id).first()
            if not plant:
                return Response(
                    {"message": f"Plant does not exist: {plant_id}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            lawn_plant = LawnPlant.objects.filter(
                lawn=lawn,
                plant=plant,
                user=user,
            ).first()

            if not lawn_plant:
                return Response(
                    {"message": f"This plant is not assigned to your lawn."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            deleted_plants.append(lawn_plant)

        # Serialize before deleting so FKs are still accessible
        response_serializer = LawnPlantSerializer(deleted_plants, many=True)
        response_data = response_serializer.data
        for item in response_data:
            if "plant" in item and item["plant"]:
                item["plant"]["image"] = parse_image_field(item["plant"].get("image"))

        for lp in deleted_plants:
            lp.delete()

        return Response(
            {
                "message": "Plants successfully removed from the lawn.",
                "data": response_data,
            },
            status=status.HTTP_200_OK,
        )


class UserLawnPlantDetailAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LawnPlantSerializer

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        user_lawn = get_object_or_404(
            UserLawn.objects.select_related("lawn"),
            user_id=user_id,
        )
        return LawnPlant.objects.filter(
            lawn=user_lawn.lawn
        ).select_related("lawn", "plant", "user")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        for item in data:
            if "plant" in item and item["plant"]:
                item["plant"]["image"] = parse_image_field(item["plant"].get("image"))
        return Response(data, status=status.HTTP_200_OK)


class RealGardenImagesAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RealGardenImagesSerializer
    queryset = RealGardenImages.objects.all().order_by("-created_at")
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

        data["image"] = image_urls if image_urls else []
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Garden images added successfully",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


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
                old_image_urls = instance.image if isinstance(instance.image, list) else json.loads(instance.image)
                for url in old_image_urls:
                    try:
                        path = url.split("/media/")[-1] if "/media/" in url else url
                        if default_storage.exists(path):
                            default_storage.delete(path)
                    except Exception:
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

            data["image"] = image_urls

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Garden images updated successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.image:
            image_urls = instance.image if isinstance(instance.image, list) else json.loads(instance.image)
            for url in image_urls:
                try:
                    path = url.split("/media/")[-1] if "/media/" in url else url
                    if default_storage.exists(path):
                        default_storage.delete(path)
                except Exception:
                    pass

        instance.delete()
        return Response(
            {"detail": "Post deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )