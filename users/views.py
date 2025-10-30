import traceback
from collections import OrderedDict

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from plant.models import PlantRegion
from plant.serializers import PlantSerializer

from .models import *
from .serializers import *

User = get_user_model()


class CustomRegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomRegisterSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            try:
                user = serializer.save(request)

                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                verification_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"

                try:
                    send_mail(
                        subject="Verify Your Email",
                        message=render_to_string(
                            "account/email/email_verification.html",
                            {
                                "user": user,
                                "verification_url": verification_url,
                            },
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                    )
                except:
                    print("Unable to sent email for some reason")
                
                return Response(
                   {"detail": "Registration successful. Please verify your email."},
                   status=status.HTTP_201_CREATED,
                  )
            except Exception as e:
                print(f"Error inserting {e}")
        
        else:
            traceback.print_exc()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerifyView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.verified = True
                user.save()
                return render(
                    request,
                    "account/email/email_verified.html",
                    {"login_url": f"{settings.FRONTEND_URL}/login/"},
                )
            return Response(
                {"detail": "Invalid verification token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST
            )


class CustomLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = serializer.user
            if user:
                if user.verified:
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
                    data = serializer.validated_data
                    response_data = OrderedDict(
                        [
                            ("refresh", str(refresh)),
                            ("access", str(refresh.access_token)),
                            ("username", data.get("username")),
                            ("uid", data.get("uid")),
                            ("email", data.get("email")),
                            ("full_name", data.get("full_name")),
                            ("region", data.get("region")),
                            ("image", data.get("image")),
                            ("bio", data.get("bio")),
                            ("share_profile", data.get("share_profile")),
                            ("share_garden", data.get("share_garden")),
                        ]
                    )
                    return Response(response_data, status=status.HTTP_200_OK)
                return Response(
                    {"detail": "Please verify your email first"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(
                {"detail": "No active account found with the given credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(
            {"detail": "No active account found with the given credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data["new_password1"])
            request.user.save()
            return Response(
                {"detail": "Password changed successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data["email"])
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = (
                    f"{settings.FRONTEND_URL}/password/reset/confirm/{uid}/{token}/"
                )

                send_mail(
                    subject="Password Reset Request",
                    message=render_to_string(
                        "account/email/password_reset.html",
                        {
                            "user": user,
                            "reset_url": reset_url,
                        },
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )

                return Response(
                    {"detail": "Password reset email sent"}, status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                return Response(
                    {"detail": "No account found with this email"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmHTMLView(View):
    def get(self, request, uidb64, token):
        return render(
            request, "password_reset_form.html", {"uidb64": uidb64, "token": token}
        )

    def post(self, request, uidb64, token):
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        context = {"uidb64": uidb64, "token": token}

        if password1 != password2:
            context["error"] = ["Passwords do not match."]
            return render(request, "password_reset_form.html", context)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                context["error"] = ["Invalid or expired token."]
                return render(request, "password_reset_form.html", context)

            try:
                validate_password(password1, user)
            except ValidationError as ve:
                context["error"] = ve.messages
                return render(request, "password_reset_form.html", context)

            user.set_password(password1)
            user.save()
            context["success"] = True
            return render(request, "password_reset_form.html", context)

        except User.DoesNotExist:
            context["error"] = ["Invalid user."]
            return render(request, "password_reset_form.html", context)


class RegionCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RegionSerializer
    queryset = Region.objects.all()


class RegionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = RegionSerializer
    queryset = Region.objects.all()
    lookup_field = "id"


class GetPlantsByUserRegion(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserRegionPlantSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username_ = request.user

            try:
                region = UserRegion.objects.get(user_username=username_).region
            except:
                return Response({"message": "Region not found for this user."})

            try:
                plant_regions = PlantRegion.objects.filter(region=region)
            except:
                return Response({"message": "Plant Region not found."})

            plants = []

            for obj in plant_regions:
                plants.append(obj.plant)

            plant_serializer = PlantSerializer(plants, many=True)

            return Response(plant_serializer.data)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = []

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
            return Response(
                {"error": "FCM token is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        UserFCMToken.objects.update_or_create(
            user=request.user, defaults={"fcm_token": fcm_token}
        )
        return Response({"detail": "FCM token updated successfully."})
