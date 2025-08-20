import logging
import os
import logging
from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_process_init

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

app = Celery("myproject")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.timezone = "UTC"
app.conf.broker_url = "redis://localhost:6379/0"

app.autodiscover_tasks()

logger = logging.getLogger(__name__)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

app.conf.beat_schedule = {
    "run-watering-notification-daily": {
        "task": "tasks.tasks.send_watering_notification",
        "schedule": crontab(hour=10, minute=0),  # Daily at 10:00 AM
        "args": (),
    },

    "send-fertilizing-notifications": {
        "task": "tasks.tasks.send_fertilizing_notifications",
<<<<<<< HEAD
        "schedule": crontab(hour=10, minute=0),
        "args": (),
    },
    "send-monthly-pest-check": {
        "task": "tasks.tasks.send_monthly_pest_check",
        "schedule": crontab(
            day_of_month=6, hour=10, minute=0
        ),  # 6th of each month at 10:00 AM
=======
        "schedule": crontab(hour=12, minute=0),
>>>>>>> 6fd1b5310ddcbeab11640bb33d5cdc119b99fa0d
        "args": (),
    },

    "send-trimming-notifications": {
        "task": "tasks.tasks.send_trimming_notifications",
        "schedule": crontab(hour=14, minute=0),
        "args": (),
    },
    
    "send-monthly-pest-check": {
        "task": "tasks.tasks.send_monthly_pest_check",
        "schedule": crontab(hour=10, minute=0),
        "args": (),
    },

    "send_seasonal_plant_notification": {
        "task": "tasks.tasks.send_seasonal_plant_notification",
        "schedule": crontab(hour=10, minute=0),
        "args": (),
    },
<<<<<<< HEAD
    "send_seasonal_plant_suggestion": {
        "task": "tasks.tasks.send_seasonal_plant_suggestions",
        "schedule": crontab(hour=10, minute=0,day_of_month="1,16"),
        "args": (),
    },
     "send_gardening_tips": {
        "task": "tasks.tasks.send_gardening_tips",
        "schedule": crontab(hour=10, minute=0,day_of_month="1,16"),
        "args": (),
    },
}
=======
>>>>>>> 6fd1b5310ddcbeab11640bb33d5cdc119b99fa0d

    "send_gardening_tip_notification": {
        "task": "tasks.tasks.send_weekly_gardening_tip",
        "schedule": crontab(hour=10, minute=0),
        "args": (),
    },

    "mindful_gardening_notification": {
        "task": "tasks.tasks.mindful_gardening_prompt",
        "schedule": crontab(hour=10, minute=0),
        "args": (),
    },

    "photo_prompt_notification": {
        "task": "tasks.tasks.photo_prompt",
        "schedule": crontab(hour=10, minute=0),
        "args": (),
    },

    "morning_in_the_garden_notification": {
        "task": "tasks.tasks.morning_in_the_garden",
        "schedule": crontab(hour=7, minute=0),
        "args": (),
    },

    "nature_break_notification": {
        "task": "tasks.tasks.nature_break",
        "schedule": crontab(hour=10, minute=0),
        "args": (),
    },

    "touch_of_green_notification": {
        "task": "tasks.tasks.touch_of_green",
        "schedule": crontab(hour=10, minute=0),
        "args": (),
    },

    "mindful_moment_notification": {
        "task": "tasks.tasks.mindful_moment",
        "schedule": crontab(hour=10, minute=0),
        "args": (),
    },

    "tiny_care_notification": {
        "task": "tasks.tasks.tiny_care",
        "schedule": crontab(hour=10, minute=0),
        "args": (),
    },

    "garden_vibes_notification": {
        "task": "tasks.tasks.garden_vibes",
        "schedule": crontab(hour=10, minute=0),
        "args": (),
    },

}