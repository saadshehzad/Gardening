import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from firebase_admin.messaging import Message, Notification, send
from django.utils import timezone
from datetime import timedelta
from myproject import fcm_config

from plant.models import Plant
from django_redis import get_redis_connection
from notifications.models import FCMNotification
from users.models import UserFCMToken

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
        print(
            f"FCM token Found, send notification to {user.username}: {token.fcm_token}"
        )
        message = Message(
            notification=Notification(
                title="Watering Reminder",
                body=f"It's time to water your plants, {user.username}!",
            ),
            token=token.fcm_token,
        )
        try:
            send(message)
            FCMNotification.objects.create(
                type="Watering",
                title="Watering Reminder",
                message=f"Sent watering reminder to {user.username}",
                sent=True,
                user=user,
            )
        except Exception as e:
            logger.error(f"Failed to send notification to {user.username}: {e}")


@shared_task
def send_fertilizing_notifications():
    today = timezone.now()
    redis_conn = get_redis_connection("default")
    
    try:
        users = User.objects.all()  
    except User.DoesNotExist:
        return

    plants = Plant.objects.filter(fertilizer_interval__isnull=False)

    for plant in plants:
        for user in users:
            redis_key = f"fertilizing_notification:{plant.id}:{user.id}"
            next_notification_str = redis_conn.get(redis_key)
            if next_notification_str:
                next_notification = timezone.datetime.fromisoformat(next_notification_str.decode())
            else:
                last_notification = plant.last_notification_send_date.get("Fertilizing")
            if last_notification:
                try:
                    next_notification = timezone.datetime.strptime(last_notification, "%Y-%m-%d %H:%M:%S")
                    next_notification = timezone.make_aware(next_notification)
                except ValueError:
                    next_notification = today
            else:
                next_notification = today

        if not next_notification or today >= next_notification:
            send_fertilizing_notification(user, plant)
            try:
                interval_days = int(plant.fertilizer_interval)
                next_notification = today + timedelta(days=interval_days)
                redis_conn.set(redis_key, next_notification.isoformat())
                plant.last_notification_send_date = {
                    "Fertilizing": next_notification.strftime("%Y-%m-%d %H:%M:%S")
                }
                plant.save()
            except:
                pass


def send_fertilizing_notification(user, plant):
    tokens = UserFCMToken.objects.filter(user=user)
    if not tokens.exists():
        return

    for token in tokens:
        message = Message(
            notification=Notification(
                title="Fertilizing Reminder",
                body=f"It's time to fertilize your {plant.name}, {user.username}!",
            ),
            token=token.fcm_token,
        )
        try:
            send(message)
            FCMNotification.objects.create(
                type="Fertilizing",
                title="Fertilizing Reminder",
                message=f"Sent fertilizing reminder for {plant.name} to {user.username}",
                sent=True,
                user=user,
            )
        except:
            pass


@shared_task
def send_monthly_pest_check():
    today = timezone.now().date()
    if today.day != 6:
        return

    users = User.objects.all()
    for user in users:
        tokens = UserFCMToken.objects.filter(user=user)
        if not tokens.exists():
            continue

        for token in tokens:
            message = Message(
                notification=Notification(
                    title="Pest Check Reminder",
                    body=f"It's time for your monthly pest check, {user.username}!",
                ),
                token=token.fcm_token,
            )
            try:
                send(message)
                FCMNotification.objects.create(
                    type="Pest Check",
                    title="Pest Check Reminder",
                    message=f"Sent pest check reminder to {user.username}",
                    sent=True,
                    user=user,
                )
            except Exception as e:
                logger.error(f"Failed to send notification to {user.username} for token {token.fcm_token}: {str(e)}")