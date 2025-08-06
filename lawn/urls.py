from django.urls import path

from .views import *

urlpatterns = [
    path("list/", LawnListCreateAPIView.as_view()),
    path(
        "lawnLocation/",
        UserLawnRetrieveUpdateAPIView.as_view(),
        name="user-lawn-retrieve",
    ),
    path("list/<uuid:id>/", LawnDetailAPIView.as_view()),
    path("products/", UserLawnPlantAPIView.as_view()),
    path("garden/", RealGardenImagesAPIView.as_view()),
    path("garden/<int:pk>/", RealGardenImagesDetailAPIView.as_view()),
]
