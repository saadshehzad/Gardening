from django.urls import path

from plant.views import *

urlpatterns = [
    path("categorylist/", CategoryCreateAPIView.as_view()),
    path("categorydetail/<uuid:id>/", CategoryDetailAPIView.as_view()),
    path("productlist/", PlantCreateAPIView.as_view()),
    path("productdetail/<uuid:id>/", PlantDetailAPIView.as_view()),
]
