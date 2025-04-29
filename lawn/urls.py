from django.urls import path

from .views import *

urlpatterns = [
    path("list/", LawnListCreateAPIView.as_view()),
    path("list/<uuid:id>/", LawnDetailAPIView.as_view()),
    path("products/", UserLawnProductAPIView.as_view()),
    path("garden/", RealGardenImagesAPIView.as_view()),
    path("garden/<int:pk>/", RealGardenImagesDetailAPIView.as_view()),
]
