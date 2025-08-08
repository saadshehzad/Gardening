from .tasks import *
from notifications.models import *
from plant.models import *
from users.models import UserFCMToken

def send_watering_notification_to_user(user):
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
                body=f"It's time to water your Garden, {user.username}!",
            ),
            token=token.fcm_token,
            data={
                "type": "Generic",
            }
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


def send_fertilizing_notification(user, plant):
    tokens = UserFCMToken.objects.filter(user=user)
    if not tokens.exists():
        return False

    success = False
    for token in tokens:
        message = Message(
            notification=Notification(
                title="Fertilizing Reminder",
                body=f"It's time to fertilize your {plant.name}!",
            ),
            token=token.fcm_token,
            data={
                "type": "fertilizing_reminder",
                "plant_id": str(plant.id),
            }
        )
        try:
            send(message)
            success = True
        except Exception as e:
            logger.error(f"Failed to send fertilizing notification: {e}")
            continue
    
    # Create notification record
    if success:
        FCMNotification.objects.create(
            type="Fertilizing",
            title="Fertilizing Reminder",
            message=f"It's time to fertilize your {plant.name}!",
            sent=True,
            user=user,
        )
    
    return success




def send_trimming_notification(user, plant):
    tokens = UserFCMToken.objects.filter(user=user)
    if not tokens.exists():
        return False

    success = False
    for token in tokens:
        message = Message(
            notification=Notification(
                title="Trimming Reminder",
                body=f"It's time to trim your {plant.name}!",
            ),
            token=token.fcm_token,
            data={
            "type": "trimming_reminder",
            "plant_id": str(plant.id)
        }
        )
        try:
            send(message)
            success = True
        except Exception as e:
            logger.error(f"Failed to send trimming notification: {e}")
            continue
    
    # Create notification record
    if success:
        FCMNotification.objects.create(
            type="Trimming",
            title="Trimming Reminder",
            message=f"It's time to trim your {plant.name}!",
            sent=True,
            user=user,
        )
    
    return success