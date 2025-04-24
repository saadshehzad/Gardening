from django.urls import path

from posts.views import *

urlpatterns = [
    path("userpost/", PostListCreateAPIView.as_view()),
    path("article/", ArticlesListCreateAPIView.as_view()),
    path("report/",ReportProblemListCreateAPIView.as_view(),name='report-problem'),
    path("share/<str:pk>/", UserPostShareAPIView.as_view(), name="userpost-share"),
    path("like/<str:pk>/", UserPostLikeAPIView.as_view(), name="userpost-like"),
    path("comment/<str:pk>/", UserPostCommentAPIView.as_view(), name="userpost-comment"),
]