from django.shortcuts import render
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


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_field = "id"
