from django.urls import path
from .views import (
    LawnListCreateAPIView,
    MyLawnRetrieveUpdateAPIView,
    UserLawnDetailAPIView,
    LawnDetailAPIView,
    MyLawnPlantAPIView,
    UserLawnPlantDetailAPIView,
    RealGardenImagesAPIView,
    RealGardenImagesDetailAPIView,
)

urlpatterns = [
    path("list/", LawnListCreateAPIView.as_view(), name="lawn-list-api"),

    # my lawn
    path("my-lawn/", MyLawnRetrieveUpdateAPIView.as_view(), name="my-lawn"),

    # another user's lawn
    path("user/<int:user_id>/lawn/", UserLawnDetailAPIView.as_view(), name="user-lawn-detail"),

    path("list/<uuid:id>/", LawnDetailAPIView.as_view(), name="lawn-detail"),

    # my lawn plants
    path("my-lawn/plants/", MyLawnPlantAPIView.as_view(), name="my-lawn-plants"),

    # another user's lawn plants
    path("user/<int:user_id>/lawn/plants/", UserLawnPlantDetailAPIView.as_view(), name="user-lawn-plants"),

    path("garden/", RealGardenImagesAPIView.as_view(), name="garden-image"),
    path("garden/<int:pk>/", RealGardenImagesDetailAPIView.as_view(), name="garden-image-detail"),
]