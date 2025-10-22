from django.urls import path

from .views import *

urlpatterns = [
    path("list/", LawnListCreateAPIView.as_view(),name="lawn-list-api"),
    path(
        "lawnLocation/",
        UserLawnRetrieveUpdateAPIView.as_view(),
        name="user-lawn-retrieve",
    ),
    path("list/<uuid:id>/", LawnDetailAPIView.as_view(),name="lawn-detail"),
    path("products/", UserLawnPlantAPIView.as_view(), name="user-lawn-API-view"),
    path("garden/", RealGardenImagesAPIView.as_view(),name="garden-image"),
    path("garden/<int:pk>/", RealGardenImagesDetailAPIView.as_view(),name="garden-image-detail"),
]
