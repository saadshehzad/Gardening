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
from lawn.models import UserLawn
from .plant_care import (send_fertilizing_notification,
                         send_trimming_notification,
                         send_watering_notification_to_user)
import random

logger = logging.getLogger(__name__)


User = get_user_model()


@shared_task
def send_watering_notification():
    users = User.objects.all()
    for user in users:
        send_watering_notification_to_user(user)


@shared_task
def send_fertilizing_notifications():
    today = timezone.now()
    redis_conn = get_redis_connection("default")
    user_lawns = UserLawn.objects.filter(
        lawn__lawnplant__plant__fertilizer_interval__isnull=False,
    ).select_related('user', 'lawn').distinct()
    
    for user_lawn in user_lawns:
        user = user_lawn.user
        lawn = user_lawn.lawn
        plants = Plant.objects.filter(lawnplant__lawn=lawn).distinct()
        
        for plant in plants:
            redis_key = f"fertilizing_notification:{plant.id}:{user.id}"
            next_notification_str = redis_conn.get(redis_key)
            if next_notification_str:
                next_notification = timezone.datetime.fromisoformat(next_notification_str.decode())
                next_notification = timezone.make_aware(next_notification) if timezone.is_naive(next_notification) else next_notification
            else:
                notification_data = plant.notification_send_date_and_type or {}
                last_notification_str = notification_data.get(f"Fertilizing_{user.id}")
                
                if last_notification_str:
                    try:
                        last_notification = timezone.datetime.fromisoformat(last_notification_str)
                        last_notification = timezone.make_aware(last_notification) if timezone.is_naive(last_notification) else last_notification
                        interval_days = int(plant.fertilizer_interval)
                        next_notification = last_notification + timedelta(days=interval_days)
                    except (ValueError, TypeError):
                        next_notification = today
                else:
                    next_notification = today  
            
            if today >= next_notification:
                success = send_fertilizing_notification(user, plant)
                
                if success:
                    try:
                        interval_days = int(plant.fertilizer_interval)
                        next_notification_date = today + timedelta(days=interval_days)
                    
                        redis_conn.set(redis_key, next_notification_date.isoformat(), ex=86400 * interval_days * 2)
                        notification_data = plant.notification_send_date_and_type or {}
                        notification_data[f"Fertilizing_{user.id}"] = next_notification_date.isoformat()
                        plant.notification_send_date_and_type = notification_data
                        plant.save(update_fields=['notification_send_date_and_type'])
                    except (ValueError, TypeError):
                        continue

"""We'll use this code  if we want to use the shared task decorator for send_fertilizing_notifications as every minute."""

# @shared_task
# def send_fertilizing_notifications():
#     today = timezone.now()
    
#     # Get users who have lawns with plants
#     user_lawns = UserLawn.objects.filter(
#         lawn__lawnplant__plant__isnull=False
#     ).select_related('user', 'lawn').distinct()
    
#     for user_lawn in user_lawns:
#         user = user_lawn.user
#         lawn = user_lawn.lawn
#         # Get plants in this user's lawn
#         plants = Plant.objects.filter(lawnplant__lawn=lawn).distinct()
        
#         for plant in plants:
#             success = send_fertilizing_notification(user, plant)
            
#             if success:
#                 notification_data = plant.notification_send_date_and_type or {}
#                 notification_data[f"Fertilizing_{user.id}"] = today.isoformat()
#                 plant.notification_send_date_and_type = notification_data
#                 plant.save(update_fields=['notification_send_date_and_type'])

@shared_task
def send_trimming_notifications():
    today = timezone.now()
    redis_conn = get_redis_connection("default")

    users = User.objects.all()
    plants = Plant.objects.filter(trimming_interval__isnull=False)
    for plant in plants:
        for user in users:
            redis_key = f"trimming_notification:{plant.id}:{user.id}"

            # Check Redis first
            next_notification_str = redis_conn.get(redis_key)
            if next_notification_str:
                next_notification = timezone.datetime.fromisoformat(
                    next_notification_str.decode()
                )
                next_notification = (
                    timezone.make_aware(next_notification)
                    if timezone.is_naive(next_notification)
                    else next_notification
                )
            else:
                # Check plant's notification field
                notification_data = plant.notification_send_date_and_type or {}
                last_notification_str = notification_data.get(f"Trimming_{user.id}")

                if last_notification_str:
                    try:
                        last_notification = timezone.datetime.fromisoformat(
                            last_notification_str
                        )
                        last_notification = (
                            timezone.make_aware(last_notification)
                            if timezone.is_naive(last_notification)
                            else last_notification
                        )
                        interval_days = int(plant.trimming_interval)
                        next_notification = last_notification + timedelta(
                            days=interval_days
                        )
                    except (ValueError, TypeError):
                        next_notification = today
                else:
                    next_notification = today  # First notification

            # Send notification if it's time
            if today >= next_notification:
                success = send_trimming_notification(user, plant)

                if success:
                    try:
                        interval_days = int(plant.trimming_interval)
                        next_notification_date = today + timedelta(days=interval_days)

                        # Store in Redis
                        redis_conn.set(
                            redis_key,
                            next_notification_date.isoformat(),
                            ex=86400 * interval_days * 2,
                        )

                        # Update plant's notification field
                        notification_data = plant.notification_send_date_and_type or {}
                        notification_data[f"Trimming_{user.id}"] = (
                            next_notification_date.isoformat()
                        )
                        plant.notification_send_date_and_type = notification_data
                        plant.save(update_fields=["notification_send_date_and_type"])
                    except (ValueError, TypeError):
                        continue


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
                    body=f"Hello {user.username}, in this {current_season} season this is the best time to plant {plants_list}",
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

seasonal_plant_suggestions = {
    "Spring": [
        "Plant strawberries for early summer treats",
        "Grow chamomile for calming tea",
        "Sow peas — they love cool weather"
    ],
    "Summer": [
        "Grow cherry tomatoes for salads",
        "Plant watermelon for a sweet snack",
        "Grow lavender for fragrance"
    ],
    "Autumn": [
        "Plant garlic now for next year's bulbs",
        "Grow coriander — loves cooler weather",
        "Sow broad beans for early spring crops"
    ],
    "Winter": [
        "Start lettuce indoors for fresh greens",
        "Grow rosemary in pots for year-round herbs",
        "Plant thyme — thrives even in cold months"
    ]
}

@shared_task
def send_seasonal_plant_suggestions():
    today = timezone.now().date()

    current_season = Season.objects.filter(
        from_date__lte= today, to_date__gte=today
    ).first()
    if not current_season:
        return

    current_suggestions = seasonal_plant_suggestions.get(current_season.name, [])
    if current_suggestions:
        suggestion = random.choice(current_suggestions)
    else:
        suggestion = "No seasonal suggestions available"

    users = User.objects.all()
    for user in users:
        tokens = UserFCMToken.objects.filter(user=user)
        if not tokens.exists():
            continue

        for token in tokens:
            message = Message(
                notification=Notification(
                    title="Seasonal Plant",
                    body=f"Hello {user.username}, {suggestion}",
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

gardening_tips = [
    "Water your plants early in the morning to reduce evaporation.",
    "Use coffee grounds to enrich your soil with nitrogen.",
    "Companion planting: grow basil near tomatoes to improve flavor and repel pests.",
    "Mulch around plants to retain moisture and prevent weeds.",
    "Rotate your crops each season to maintain soil health.",
    "Check the underside of leaves for early signs of pests."
]

@shared_task
def send_gardening_tips():
    today = timezone.now().date()
    if today.day != 6:
        return
    
    tip = random.choice(gardening_tips)

    users = User.objects.all()
    for user in users:
        tokens = UserFCMToken.objects.filter(user=user)
        if not tokens.exists():
            continue

        for token in tokens:
            message = Message(
                notification=Notification(
                    title="Seasonal Plant",
                    body=f"Hello {user.username}, {tip}",
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