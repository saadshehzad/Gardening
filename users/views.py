from allauth.account.views import ConfirmEmailView
from dj_rest_auth.registration.views import RegisterView
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from plant.models import ProductRegion
from plant.serializers import ProductSerializer

from .models import *
from .serializers import *



class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


class CustomConfirmEmailView(ConfirmEmailView):
    def get(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm(self.request)
        return render(self.request, "account/email/email_confirm.html")


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegionCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RegionSerializer
    queryset = Region.objects.all()


class RegionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = RegionSerializer
    queryset = Region.objects.all()
    lookup_field = "id"


class GetProductsByUserRegion(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserRegionProductSerialzier

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username_ = request.user

            try:
                region = UserRegion.objects.get(user_username=username_).region
            except:
                return Response({"message": "Region not found for this user."})

            try:
                product_regions = ProductRegion.objects.filter(region=region)
            except:
                return Response({"message": "Product Region not found."})

            products = []

            for obj in product_regions:
                products.append(obj.product)

            product_serializer = ProductSerializer(products, many=True)

            return Response(product_serializer.data)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            serializer = UserProfileSerializer(profile, context={"request": request})
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if UserProfile.objects.filter(user=request.user).exists():
            return Response(
                {"error": "Profile already exists. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UserProfileSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(
            profile, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateFCMTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        fcm_token = request.data.get("fcm_token")
        if not fcm_token:
            return Response({"error": "FCM token is required."}, status=status.HTTP_400_BAD_REQUEST)

        UserFCMToken.objects.update_or_create(user=request.user, defaults={"fcm_token": fcm_token})
        return Response({"success": "FCM token updated successfully."})