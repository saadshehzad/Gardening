from django.urls import path

from posts.views import *

urlpatterns = [
    path("userpost/", PostListCreateAPIView.as_view()),
    path("article/", ArticlesListCreateAPIView.as_view()),
    path("report/",ReportProblemListCreateAPIView.as_view(),name='report-problem'),
]
