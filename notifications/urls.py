from django.urls import path

from .views import UserNotificationsAPIView,MarkAllNotificationsReadAPIView,MarkNotificationReadAPIView

urlpatterns = [
    path(
        "get_notifications/",
        UserNotificationsAPIView.as_view(),
        name="user-notifications",
    ),
    path("mark_all_read/",MarkAllNotificationsReadAPIView.as_view(),name="mark-all-notifications-read"),
    path("mark_read/<uuid:id>/",MarkNotificationReadAPIView.as_view(),name="mark-notification-read"),
]
