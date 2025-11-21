import ast
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import *
from .serializers import *


class CategoryCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


    def post(self, request):
        category_id = request.data.get("category_id")

        if not category_id:
            return Response(
                {"error": "category_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not Plant.objects.filter(id=category_id).exists():
            plants_qs = Plant.objects.filter(category_id=category_id)
            return Response(
                {"error": "Plant Category not found."}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(PlantSerializer(plants_qs, many=True).data)


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
        try:
            print("=============================================")
            category_id = request.query_params.get("category_id")
            print("========", category_id)

            if category_id:
                plants_qs = Plant.objects.filter(category=category_id)
                print("plant_qs", "========")
                data = [{**item, "image": ast.literal_eval(item["image"])} for item in PlantSerializer(plants_qs, many=True).data]
                return Response(data)
            else:
                plants_qs = Plant.objects.all()
                print("plant_qs", "*********************")

                serializer_data = PlantSerializer(plants_qs, many=True).data
                data = []

                for item in serializer_data:
                    print("Item", item)
                    item["image"] = ast.literal_eval(item["image"])
                    data.append(item)

                return Response(data)

                # plants_qs = Plant.objects.all()
                # print("plant_qs", "*********************")
                # data = [{**item, "image": ast.literal_eval(item["image"])} for item in PlantSerializer(plants_qs, many=True).data]
                # return Response(data)
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()

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


class PlantDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PlantSerializer
    queryset = Plant.objects.all()
    lookup_field = "id"