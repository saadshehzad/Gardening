from django.urls import path
from .views import UserNotificationsAPIView

urlpatterns = [
    path('get_notifications/', UserNotificationsAPIView.as_view(), name='user-notifications'),
]
