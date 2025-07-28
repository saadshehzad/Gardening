from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (CustomLoginView, CustomRegisterView, EmailVerifyView,
                         PasswordChangeView, PasswordResetConfirmHTMLView,
                         PasswordResetView)

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
    path("auth/registration/", CustomRegisterView.as_view(), name="register"),
    path(
        "verify-email/<str:uidb64>/<str:token>/",
        EmailVerifyView.as_view(),
        name="verify-email",
    ),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/", CustomLoginView.as_view(), name="login"),
    path("auth/password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("auth/password/reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>/",
        PasswordResetConfirmHTMLView.as_view(),
        name="password_reset_confirm",
    ),
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
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
