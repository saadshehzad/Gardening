import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from django_redis import get_redis_connection
from firebase_admin.messaging import Message, Notification, send
from plant.models import Plant
from myproject import fcm_config
from notifications.models import FCMNotification
from plant.models import *
from users.models import UserFCMToken
from lawn.models import  LawnPlant
from .plant_care import (send_fertilizing_notification,
                         send_trimming_notification,
                         send_watering_notification_to_user)

logger = logging.getLogger(__name__)


User = get_user_model()


@shared_task
def send_watering_notification():
    users = User.objects.all()
    for user in users:
        send_watering_notification_to_user(user)


@shared_task
def send_fertilizing_notifications():
    today = timezone.now().date()

    lawn_plants = LawnPlant.objects.all()
    for lp in lawn_plants:
        user = lp.user
        plant = lp.plant

        if not plant.fertilizer_interval:
            continue

        try:
            interval_days = int(plant.fertilizer_interval)
        except ValueError:
            logger.warning(f"Invalid fertilizer_interval for plant {plant.name}")
            continue

        notif_data = plant.notification_send_date_and_type or {}
        last_sent_date = notif_data.get("fertilizing")

        if not last_sent_date:
            if send_fertilizing_notification(user, plant):
                notif_data["fertilizing"] = today.strftime("%Y-%m-%d")
                plant.notification_send_date_and_type = notif_data
                plant.save(update_fields=["notification_send_date_and_type"])
                logger.info(f"Sent first fertilizing notification to {user.username} for {plant.name}")
            continue

        # Calculate next due date from last sent date
        last_sent = timezone.datetime.strptime(last_sent_date, "%Y-%m-%d").date()
        next_due_date = last_sent + timedelta(days=interval_days)

        if today >= next_due_date:
            if send_fertilizing_notification(user, plant):
                notif_data["fertilizing"] = today.strftime("%Y-%m-%d")
                plant.notification_send_date_and_type = notif_data
                plant.save(update_fields=["notification_send_date_and_type"])
                logger.info(f"Sent fertilizing notification to {user.username} for {plant.name}")


@shared_task
def send_trimming_notifications():
    today = timezone.now()
    users = User.objects.all()
    for user in users:
        user_lawn_plants = LawnPlant.objects.filter(user=user)
        for lp in user_lawn_plants:
            plant = lp.plant
            if not plant.trimming_interval:
                continue

            try:
                interval_days = int(plant.trimming_interval)
            except ValueError:
                logger.warning(f"Invalid trimming_interval for plant {plant.name}")
                continue

            notif_data = plant.notification_send_date_and_type or {}
            last_sent_date = notif_data.get("trimming")

            if not last_sent_date:
                if send_trimming_notification(user, plant):
                    notif_data["trimming"] = today.strftime("%Y-%m-%d")
                    plant.notification_send_date_and_type = notif_data
                    plant.save(update_fields=["notification_send_date_and_type"])
                    logger.info(f"Sent first trimming notification to {user.username} for {plant.name}")
                continue

            last_sent = timezone.datetime.strptime(last_sent_date, "%Y-%m-%d")
            next_due_date = (last_sent + timedelta(days=interval_days)).date()  
            

            if today.date() >= next_due_date:
                if send_trimming_notification(user, plant):
                    notif_data["trimming"] = today.strftime("%Y-%m-%d")
                    plant.notification_send_date_and_type = notif_data
                    plant.save(update_fields=["notification_send_date_and_type"])
                    logger.info(f"Sent trimming notification to {user.username} for {plant.name}")


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
                data={
                    "type": "Generic",
                },
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
                logger.error(
                    f"Failed to send notification to {user.username} for token {token.fcm_token}: {str(e)}"
                )


@shared_task
def send_seasonal_plant_notification():
    today = timezone.now().date()

    current_season = Season.objects.filter(
        from_date__lte=today, to_date__gte=today
    ).first()
    if not current_season:
        return

    seasonal_plants = SeasonalPlant.objects.filter(season=current_season)
    seasonal_plant_names = []
    for plant in seasonal_plants:
        seasonal_plant_names.append(plant.name)

    plants_list = (
        ", ".join(seasonal_plant_names)
        if seasonal_plant_names
        else "No seasonal plants available"
    )
    users = User.objects.all()
    for user in users:
        tokens = UserFCMToken.objects.filter(user=user)
        if not tokens.exists():
            continue

        for token in tokens:
            message = Message(
                notification=Notification(
                    title="Seasonal Plant",
                    body=f"Hello {user.username}, here are seasonal plants for you: {plants_list}",
                ),
                token=token.fcm_token,
            )
            try:
                send(message)
                FCMNotification.objects.create(
                    type="Seasonal Plant",
                    title="Seasonal Plant Reminder",
                    message=f"Sent Seasonal Plants to {user.username}",
                    sent=True,
                    user=user,
                )
            except Exception as e:
                logger.error(
                    f"Failed to send notification to {user.username} for token {token.fcm_token}: {str(e)}"
                )
