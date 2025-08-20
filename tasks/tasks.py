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


@shared_task
def send_weekly_gardening_tip():
    today = timezone.now().date()
    if today.day != 3:
        return


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

                    title="Gardening Tip",
                    body=f"Tip of the week: Mix crushed eggshells into your soil for extra calcium!",
                token=token.fcm_token,
                data={
                    "type": "Generic",
                },
            )
            try:
                send(message)
                FCMNotification.objects.create(

                    type="Seasonal Plant",
                    title="Seasonal Plant Reminder",
                    message=f"Sent Seasonal Plants to {user.username}",

                    type="Gardening Tip",
                    title="Gardening Tip",
                    message=f"Sent gardening tip to {user.username}",

                    sent=True,
                    user=user,
                 )
            except Exception as e:
                logger.error(
                    f"Failed to send notification to {user.username} for token {token.fcm_token}: {str(e)}"
                )

@shared_task
def mindful_gardening_prompt():
    today = timezone.now().date()
    if today.day != 9:
        return

    users = User.objects.all()
    for user in users:
        tokens = UserFCMToken.objects.filter(user=user)
        if not tokens.exists():
            continue

        for token in tokens:
            message = Message(
                notification=Notification(
                    title="Mindful Gardening Prompt",
                    body=f"Step outside, take a breath, and spend 5 minutes with your plants today.",
                ),
                token=token.fcm_token,
                data={
                    "type": "Generic",
                },
            )
            try:
                send(message)
                FCMNotification.objects.create(
                    type="Mindful Gardening",
                    title="Get Mindful",
                    message=f"Sent mindful gardening prompt to {user.username}",
                    sent=True,
                    user=user,
                )
            except Exception as e:
                logger.error(
                    f"Failed to send notification to {user.username} for token {token.fcm_token}: {str(e)}"
                )


@shared_task
def photo_prompt():
    today = timezone.now().date()
    if today.day != 12:
        return

    users = User.objects.all()
    for user in users:
        tokens = UserFCMToken.objects.filter(user=user)
        if not tokens.exists():
            continue

        for token in tokens:
            message = Message(
                notification=Notification(
                    title="Photo Prompt",
                    body=f"Capture your garden's beauty—share your plant's progress with friends!",
                ),
                token=token.fcm_token,
                data={
                    "type": "Generic",
                },
            )
            try:
                send(message)
                FCMNotification.objects.create(
                    type="Photo Prompt",
                    title="Photo Prompt",
                    message=f"Sent photo prompt to {user.username}",
                    sent=True,
                    user=user,
                )
            except Exception as e:
                logger.error(
                    f"Failed to send notification to {user.username} for token {token.fcm_token}: {str(e)}"
                )


@shared_task
def morning_in_the_garden():
    today = timezone.now().date()
    if today.day != 15:
        return

    users = User.objects.all()
    for user in users:
        tokens = UserFCMToken.objects.filter(user=user)
        if not tokens.exists():
            continue

        for token in tokens:
            message = Message(
                notification=Notification(
                    title="Morning in the Garden",
                    body=f"Hey {user.username}, start your day with fresh air—step into your garden for a quick recharge.",
                ),
                token=token.fcm_token,
                data={
                    "type": "Generic",
                },
            )
            try:
                send(message)
                FCMNotification.objects.create(
                    type="Morning in the Garden",
                    title="Morning in the Garden",
                    message=f"sent morning in the garden prompt to {user.username}",
                    sent=True,
                    user=user,
                )
            except Exception as e:
                logger.error(
                    f"Failed to send notification to {user.username} for token {token.fcm_token}: {str(e)}"
                )


@shared_task
def nature_break():
    today = timezone.now().date()
    if today.day != 18:
        return

    users = User.objects.all()
    for user in users:
        tokens = UserFCMToken.objects.filter(user=user)
        if not tokens.exists():
            continue

        for token in tokens:
            message = Message(
                notification=Notification(
                    title="Nature Break",
                    body=f"Take a short break, stretch, and enjoy the beauty of your plants.",
                ),
                token=token.fcm_token,
                data={
                    "type": "Generic",
                },
            )
            try:
                send(message)
                FCMNotification.objects.create(
                    type="Nature Break",
                    title="Nature Break",
                    message=f"Sent nature break prompt to {user.username}",
                    sent=True,
                    user=user,
                )
            except Exception as e:
                logger.error(
                    f"Failed to send notification to {user.username} for token {token.fcm_token}: {str(e)}"
                )

@shared_task
def touch_of_green():
    today = timezone.now().date()
    if today.day != 21:
        return

    users = User.objects.all()
    for user in users:
        tokens = UserFCMToken.objects.filter(user=user)
        if not tokens.exists():
            continue

        for token in tokens:
            message = Message(
                notification=Notification(
                    title="Touch of Green",
                    body=f"Gardening is therapy—go touch the soil and feel grounded.",
                ),
                token=token.fcm_token,
                data={
                    "type": "Generic",
                },
            )
            try:
                send(message)
                FCMNotification.objects.create(
                    type="Touch of Green",
                    title="Touch of Green",
                    message=f"Sent touch of green prompt to {user.username}",
                    sent=True,
                    user=user,
                )
            except Exception as e:
                logger.error(
                    f"Failed to send notification to {user.username} for token {token.fcm_token}: {str(e)}"
                )


@shared_task
def mindful_moment():
    today = timezone.now().date()
    if today.day != 24:
        return

    users = User.objects.all()
    for user in users:
        tokens = UserFCMToken.objects.filter(user=user)
        if not tokens.exists():
            continue

        for token in tokens:
            message = Message(
                notification=Notification(
                    title="Mindful Moment",
                    body=f"Disconnect from screens and reconnect with your garden. Enjoy the sights, sounds, and scents of nature.",
                ),
                token=token.fcm_token,
                data={
                    "type": "Generic",
                },
            )
            try:
                send(message)
                FCMNotification.objects.create(
                    type="Mindful Moment",
                    title="Mindful Moment",
                    message=f"sent mindful moment prompt to {user.username}",
                    sent=True,
                    user=user,
                )
            except Exception as e:
                logger.error(
                    f"Failed to send notification to {user.username} for token {token.fcm_token}: {str(e)}"
                )


@shared_task
def tiny_care():
    today = timezone.now().date()
    if today.day != 27:
        return

    users = User.objects.all()
    for user in users:
        tokens = UserFCMToken.objects.filter(user=user)
        if not tokens.exists():
            continue

        for token in tokens:
            message = Message(
                notification=Notification(
                    title="Tiny Care",
                    body=f"Even 5 minutes of attention keeps your plants thriving.",
                ),
                token=token.fcm_token,
                data={
                    "type": "Generic",
                },
            )
            try:
                send(message)
                FCMNotification.objects.create(
                    type="Tiny Care",
                    title="Tiny Care",
                    message=f"Sent tiny care prompt to {user.username}",
                    sent=True,
                    user=user,
                )
            except Exception as e:
                logger.error(
                    f"Failed to send notification to {user.username} for token {token.fcm_token}: {str(e)}"
                )


@shared_task
def garden_vibes():
    today = timezone.now().date()
    if today.day != 30:
        return

    users = User.objects.all()
    for user in users:
        tokens = UserFCMToken.objects.filter(user=user)
        if not tokens.exists():
            continue

        for token in tokens:
            message = Message(
                notification=Notification(
                    title="Garden Vibes",
                    body=f"Spend time outside—let your garden be your happy place today.",
                ),
                token=token.fcm_token,
                data={
                    "type": "Generic",
                },
            )
            try:
                send(message)
                FCMNotification.objects.create(
                    type="Garden Vibes",
                    title="Garden Vibes",
                    message=f"Sent garden vibes prompt to {user.username}",
                    sent=True,
                    user=user,
                )
            except Exception as e:
                logger.error(
                    f"Failed to send notification to {user.username} for token {token.fcm_token}: {str(e)}"
                )