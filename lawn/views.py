import sys
import json
from rest_framework import generics, status, pagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from users.models import User
from .models import Lawn, UserLawn, LawnProduct, RealGardenImages, Product
from .serializers import *
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile



class LawnListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LawnSerializer
    queryset = Lawn.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if UserLawn.objects.filter(user=user).exists():
            raise ValidationError("You can only create one lawn.")
        lawn = serializer.save()
        UserLawn.objects.create(user=user, lawn=lawn)

class LawnDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LawnSerializer
    queryset = Lawn.objects.all()
    lookup_field = "id"

class UserLawnProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLawnProductSerializer

    def get(self, request, *args, **kwargs):
        """Retrieve all products in the user's lawn."""
        user = request.user
        try:
            user_lawn = UserLawn.objects.get(user=user)
            lawn_products = LawnProduct.objects.filter(lawn=user_lawn.lawn)
            serializer = LawnProductSerializer(lawn_products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserLawn.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Add products to the user's lawn."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            product_ids = serializer.validated_data['products']
            user = request.user
            user_lawn, created = UserLawn.objects.get_or_create(
                user=user,
                defaults={'lawn': Lawn.objects.create(name=f"{user.username}'s Lawn")}
            )
            lawn = user_lawn.lawn

            lawn_products = []
            for product_id in product_ids:
                try:
                    product = Product.objects.get(id=product_id)
                    if LawnProduct.objects.filter(lawn=lawn, product=product).exists():
                        return Response(
                            {"message": f"Product {product_id} is already assigned to your lawn."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    lawn_product = LawnProduct.objects.create(lawn=lawn, product=product)
                    lawn_products.append(lawn_product)
                except Product.DoesNotExist:
                    return Response(
                        {"message": f"Product with ID {product_id} does not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            response_serializer = LawnProductSerializer(lawn_products, many=True)
            return Response(
                {
                    "message": "Products successfully added to the lawn.",
                    "data": response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """Remove products from the user's lawn."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            product_ids = serializer.validated_data['products']
            user = request.user

            try:
                user_lawn = UserLawn.objects.get(user=user)
                lawn = user_lawn.lawn
            except UserLawn.DoesNotExist:
                return Response(
                    {"message": "You do not have a lawn."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            deleted_products = []
            for product_id in product_ids:
                try:
                    product = Product.objects.get(id=product_id)
                    lawn_product = LawnProduct.objects.filter(lawn=lawn, product=product).first()
                    if not lawn_product:
                        return Response(
                            {"message": f"Product with ID {product_id} is not assigned to your lawn."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    lawn_product.delete()
                    deleted_products.append(lawn_product)
                except Product.DoesNotExist:
                    return Response(
                        {"message": f"Product with ID {product_id} does not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            response_serializer = LawnProductSerializer(deleted_products, many=True)
            return Response(
                {
                    "message": "Products successfully removed from the lawn.",
                    "data": response_serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RealGardenImagesAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RealGardenImagesSerializer
    queryset = RealGardenImages.objects.all()
    pagination_class = pagination.PageNumberPagination
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
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
    
class RealGardenImagesDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RealGardenImagesSerializer
    queryset = RealGardenImages.objects.all()
    lookup_field = 'pk'

    def resize_image(self, image, max_size_mb=1):
        """
        Resize image if it exceeds max_size_mb (in MB). Returns resized image as ContentFile.
        """
        max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
        img = Image.open(image)
        
        # Convert to RGB if image is in RGBA or other modes
        if img.mode in ('RGBA', 'LA'):
            img = img.convert('RGB')
        
        # Get initial file size
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG', quality=85)
        img_size = img_buffer.tell()

        # If image size is already under max_size_bytes, return original
        if img_size <= max_size_bytes:
            img_buffer.seek(0)
            return ContentFile(img_buffer.read(), name=image.name)

        # Calculate scaling factor to reduce size
        scaling_factor = (max_size_bytes / img_size) ** 0.5
        new_width = int(img.width * scaling_factor)
        new_height = int(img.height * scaling_factor)

        # Resize image
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save with iterative quality reduction if still too large
        quality = 85
        img_buffer = BytesIO()
        while True:
            img_buffer.seek(0)
            img_buffer.truncate()
            img.save(img_buffer, format='JPEG', quality=quality)
            if img_buffer.tell() <= max_size_bytes or quality <= 10:
                break
            quality -= 5

        img_buffer.seek(0)
        return ContentFile(img_buffer.read(), name=image.name)
    
    
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        images = request.FILES.getlist("image")
        if images:
            if instance.image:
                old_image_urls = json.loads(instance.image) if isinstance(instance.image, str) else instance.image
                for url in old_image_urls:
                    try:
                        path = url.split('/media/')[-1] if '/media/' in url else url
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
                    return Response({"error": f"Failed to save image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            data["image"] = json.dumps(image_urls)
        
        serializer = self.get_serializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Post updated successfully",
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.image:
            image_urls = json.loads(instance.image) if isinstance(instance.image, str) else instance.image
            for url in image_urls:
                try:
                    path = url.split('/media/')[-1] if '/media/' in url else url
                    if default_storage.exists(path):
                        default_storage.delete(path)
                except Exception as e:
                    pass 
        
        instance.delete()
        return Response({
            "message": "Post deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)