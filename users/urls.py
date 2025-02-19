from django.urls import path

from users.views import *

urlpatterns = [
    path("regionlist/", RegionCreateAPIView.as_view()),
    path("regiondetail/<uuid:id>/", RegionDetailAPIView.as_view()),
    path("user-region-product/", GetProductsByUserRegion.as_view()),
]
