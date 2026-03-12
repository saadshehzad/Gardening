from django.urls import path

from users.views import (
    GetPlantsByUserRegion,
    RegionCreateAPIView,
    RegionDetailAPIView,
    UpdateFCMTokenView,
    UserProfileView,
)

urlpatterns = [
    path("regionlist/", RegionCreateAPIView.as_view(), name="region-list"),
    path("regiondetail/<uuid:id>/", RegionDetailAPIView.as_view(), name="region-detail"),
    path("user-region-plant/", GetPlantsByUserRegion.as_view(), name="user-region-plant"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("fcmtoken/", UpdateFCMTokenView.as_view(), name="fcm-token"),
]