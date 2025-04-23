
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from rest_framework.exceptions import ValidationError

from .models import Lawn
from .serializers import *


class LawnListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LawnSerializer
    queryset = Lawn.objects.all()
    def perform_create(self, serializer):
        user = self.request.user
        if UserLawn.objects.filter(user=user).exists():
            raise ValidationError("You can only create one lawn.")
        lawn = serializer.save()
        UserLawn.objects.create(user=user,lawn=lawn)







class LawnDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LawnSerializer
    queryset = Lawn.objects.all()
    lookup_field = "id"
    
    

    
class AddProductToUserLawn(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateUserLawnProductSerializer
    
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            user_lawn = UserLawn.objects.get(user=user)
            lawn_products = LawnProduct.objects.filter(lawn=user_lawn.lawn)
            serializer = LawnProductSerializer(lawn_products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserLawn.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)
        
        
    def post(self, request, *args, **kwargs):
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
                            {"message": f"Product is already assigned to your lawn."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    lawn_product = LawnProduct.objects.create(lawn=lawn, product=product)
                    lawn_products.append(lawn_product)
                except Product.DoesNotExist:
                    return Response(
                        {"message": f"Product with ID {product_id} does not exist."},status=status.HTTP_400_BAD_REQUEST,)
            response_serializer = LawnProductSerializer(lawn_products, many=True)
            return Response(
                {
                    "message": "Products successfully added to the lawn.",
                    "data": response_serializer.data
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DisplayProductToUserLawn(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DisplayUserLawnProductSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username_ = request.user
            print(username_)
            lawn_id = UserLawn.objects.get(user_username=username_).lawn.id
            lawn_products = LawnProduct.objects.filter(lawn__id=lawn_id)
            s = LawnProductSerializer(lawn_products, many=True)

            return Response(s.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveProductFromUserLawn(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeleteUserLawnProductSerializer

    def delete(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            product_ids = serializer.validated_data['products']
            user = request.user

            try:
                # Get the user's lawn
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
