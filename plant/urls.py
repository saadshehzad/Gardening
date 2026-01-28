from django.urls import path
from plant.views import *

urlpatterns = [
    path("categorylist/", CategoryCreateAPIView.as_view(), name="category-list"),
    path("categorydetail/<uuid:id>/", CategoryDetailAPIView.as_view(), name="category-detail"),

    path("productlist/", PlantCreateAPIView.as_view(), name="product-list-create"),
    path("productdetail/<uuid:id>/", PlantDetailAPIView.as_view(), name="product-detail"),

    path("seasonalproduct/", SeasonalPlantListAPIView.as_view(), name="seasonal-product-list"),
]