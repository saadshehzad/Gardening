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


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = "id"


class PlantCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PlantSerializer
    queryset = Plant.objects.all()

    def list(self, request, *args, **kwargs):
        qs = Plant.objects.all()

        category_id = request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(category_id=category_id)

        season = request.query_params.get("season")
        if season:
            season = season.strip().lower()
            if season == "auto":
                season = current_season_name(timezone.localdate())

            if season not in {"winter", "spring", "summer", "fall"}:
                return Response(
                    {"error": "Invalid season. Use winter/spring/summer/fall/auto."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            qs = qs.filter(seasons__name=season).distinct()

        serializer_data = PlantSerializer(qs, many=True).data
        for item in serializer_data:
            item["image"] = parse_image_field(item.get("image"))
        return Response(serializer_data, status=status.HTTP_200_OK)

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

    def get_queryset(self):
        qs = Plant.objects.all().order_by("id")

        category_id = self.request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(category_id=category_id)

        forced = self.request.query_params.get("season")
        if forced:
            season_name = forced.strip().lower()
            if season_name not in {"winter", "spring", "summer", "fall"}:
                return Plant.objects.none()
        else:
            season_name = current_season_name(timezone.localdate())

        qs = qs.filter(seasons__name=season_name).distinct()

        return qs