from celery import shared_task
from django.contrib.auth import get_user_model
from firebase_admin.messaging import Message, Notification
from users.models import UserFCMToken
from notifications.models import FCMNotification
from firebase_admin.messaging import send
from myproject import fcm_config
import logging
logger = logging.getLogger(__name__)


User = get_user_model()


@shared_task
def send_watering_notification():
    users = User.objects.all()
    for user in users:
        send_notification(user)

def send_notification(user):
    if not user:
        return

    tokens = UserFCMToken.objects.filter(user=user)
    if not tokens.exists():
        logger.warning(f"No FCM tokens found for user: {user.username}")
        return
    for token in tokens:
        message = Message(
            notification=Notification(
                title="Watering Reminder",
                body=f"It's time to water your plants, {user.username}!"
            ),
            token=token.fcm_token
        )
        try:
            send(message)
            FCMNotification.objects.create(
                type="Watering",
                title="Watering Reminder",
                message=f"Sent watering reminder to {user.username}",
                sent=True
            )
        except Exception as e:
            logger.error(f"Failed to send notification to {user.username}: {e}")