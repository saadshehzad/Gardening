import ast
import json
from datetime import date

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Category, Plant, Season
from .serializers import CategorySerializer, PlantSerializer

from rest_framework.pagination import PageNumberPagination


def parse_image_field(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        try:
            parsed = json.loads(s)
            return parsed if isinstance(parsed, list) else [parsed]
        except Exception:
            try:
                parsed = ast.literal_eval(s)
                return parsed if isinstance(parsed, list) else [parsed]
            except Exception:
                return []
    return []


class CategoryCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        image = request.FILES.get("image")

        if image:
            try:
                path = default_storage.save(f"images/categories/{image.name}", ContentFile(image.read()))
                relative_url = default_storage.url(path)
                full_url = request.build_absolute_uri(relative_url)
                data["image"] = full_url
            except Exception as e:
                return Response(
                    {"error": f"Failed to save image: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Category created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = request.data.copy()
        image = request.FILES.get("image")

        if image:
            try:
                path = default_storage.save(f"images/categories/{image.name}", ContentFile(image.read()))
                relative_url = default_storage.url(path)
                full_url = request.build_absolute_uri(relative_url)
                data["image"] = full_url
            except Exception as e:
                return Response(
                    {"error": f"Failed to save image: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Category updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class PlantCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PlantSerializer
    queryset = Plant.objects.all()

    def list(self, request, *args, **kwargs):
        qs = Plant.objects.all()

        category_id = request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(category_id=category_id)

        season_param = request.query_params.get("season")
        if season_param:
            season_name = season_param.strip().lower()
            if season_name == "auto":
                season_name = current_season_name(timezone.localdate())
        else:
            # Default to current season when no season parameter is provided
            season_name = current_season_name(timezone.localdate())

        if season_name not in {"winter", "spring", "summer", "fall"}:
            return Response(
                {"error": "Invalid season. Use winter/spring/summer/fall/auto."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = qs.filter(seasons__name=season_name).distinct()

        serializer_data = PlantSerializer(qs, many=True).data
        for item in serializer_data:
            item["image"] = parse_image_field(item.get("image"))

        return Response(
            {
                "current_season": season_name,
                "available_seasons": ["winter", "spring", "summer", "fall"],
                "plants": serializer_data,
            },
            status=status.HTTP_200_OK,
        )

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
                return Response(
                    {"error": f"Failed to save image: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        data["image"] = json.dumps(image_urls) if image_urls else "[]"

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Plant added successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlantDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PlantSerializer
    queryset = Plant.objects.all()
    lookup_field = "id"


def current_season_name(d: date) -> str:
    m = d.month
    if m in (12, 1, 2):
        return "winter"
    if m in (3, 4, 5):
        return "spring"
    if m in (6, 7, 8):
        return "summer"
    return "fall"


def current_season(d: date | None = None) -> Season:
    d = d or timezone.localdate()
    return Season.objects.get(name=current_season_name(d))


class PlantPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

class SeasonalPlantListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PlantSerializer
    pagination_class = PlantPagination

    def get_season_name(self):
        forced = self.request.query_params.get("season")
        if forced:
            season_name = forced.strip().lower()
            if season_name not in {"winter", "spring", "summer", "fall"}:
                return None
            return season_name
        return current_season_name(timezone.localdate())

    def get_queryset(self):
        qs = Plant.objects.all().order_by("id")

        category_id = self.request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(category_id=category_id)

        season_name = self.get_season_name()
        if season_name is None:
            return Plant.objects.none()

        qs = qs.filter(seasons__name=season_name).distinct()
        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        season_name = self.get_season_name() or current_season_name(timezone.localdate())

        # Parse images in results
        results = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        for item in results:
            item["image"] = parse_image_field(item.get("image"))

        if isinstance(response.data, dict):
            response.data["current_season"] = season_name
            response.data["available_seasons"] = ["winter", "spring", "summer", "fall"]
        else:
            response.data = {
                "current_season": season_name,
                "available_seasons": ["winter", "spring", "summer", "fall"],
                "results": response.data,
            }

        return response