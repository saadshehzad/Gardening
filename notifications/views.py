from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from django.utils import timezone
from .models import FCMNotification
from .serializers import NotificationSerializer
from rest_framework import status

class UserNotificationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        notifications = FCMNotification.objects.filter(
            user=request.user,
            created_at__gte=seven_days_ago
        ).order_by('-created_at')
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class MarkAllNotificationsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        FCMNotification.objects.filter(
            user=request.user, 
            is_read=False
        ).update(is_read=True)
        
        return Response({"detail": "All notifications marked as read."})
    
class MarkNotificationReadAPIView(APIView):  
    permission_classes = [IsAuthenticated]
    def patch(self, request, id):
        try:
            notification = FCMNotification.objects.get(id=id, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"detail": "Notification marked as read."}, status=status.HTTP_200_OK)
        except FCMNotification.DoesNotExist:
            return Response({"message": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)