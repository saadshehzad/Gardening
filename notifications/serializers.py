from rest_framework import serializers
from .models import FCMNotification

class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    
    class Meta:
        model = FCMNotification
        fields = ['id', 'title', 'message', 'is_read', 'created_at', 'user', 'is_read']