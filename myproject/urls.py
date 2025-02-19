from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from allauth.account.views import confirm_email 
# from users.views import CustomConfirmEmailView 
from users.views import CustomRegisterView , CustomConfirmEmailView
from django.views.generic import TemplateView
from django.urls import path, re_path
from django.views.generic import TemplateView

 
schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version="v1",
        description="API documentation for my project",
        terms_of_service="https://www.example.com/terms/", 
        contact=openapi.Contact(email="support@example.com"), 
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)



 

urlpatterns = [
    path("admin/", admin.site.urls), 
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), 
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("auth/password/change/", include("dj_rest_auth.urls")),
    path("auth/password/reset/", include("dj_rest_auth.urls")),
    path("auth/password/reset/confirm/", include("dj_rest_auth.urls")),
    path("auth/registration/", CustomRegisterView.as_view(), name="custom_register"),
    path("auth/registration/account-confirm-email/<str:key>/", CustomConfirmEmailView.as_view(), name="account_confirm_email"),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0), 
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("lawn/", include("lawn.urls")),
    path("plant/", include("plant.urls")), 
    path("users/", include("users.urls")),  
    path("posts/", include("posts.urls")),
]
