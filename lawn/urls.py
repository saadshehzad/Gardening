from django.urls import path

from .views import *

urlpatterns = [
    path("list/", LawnListCreateAPIView.as_view()),
    path("list/<uuid:id>/", LawnDetailAPIView.as_view()),
    path("addproductinuser/", AddProductToUserLawn.as_view()),
    path("displayproductinuser/", DisplayProductToUserLawn.as_view()),
]
