from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

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

    if not products_qs.exists():
        products_qs = Product.objects.filter(category_id=category_id)
        return Response(
            {"error": "Product Category not found."}, status=status.HTTP_404_NOT_FOUND
        )

    return Response(ProductSerializer(products_qs, many=True).data)


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = "id"


class ProductCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def list(self, request, *args, **kwargs):
        category_id = request.query_params.get("category_id")

        if category_id:
            products_qs = Product.objects.filter(category=category_id)
            return Response(ProductSerializer(products_qs, many=True).data)
        else:
            products_qs = Product.objects.all()
            data = ProductSerializer(products_qs, many=True)
            return Response(data.data)
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
            serializer.save()
            return Response(
                {
                    "message": "Product added successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_field = "id"


