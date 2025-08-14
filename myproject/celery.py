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
        "schedule": crontab(),
        "args": (),
    },
    "send-monthly-pest-check": {
        "task": "tasks.tasks.send_monthly_pest_check",
        "schedule": crontab(
            day_of_month=6, hour=10, minute=0
        ),  # 6th of each month at 10:00 AM
        "args": (),
    },
    "send-trimming-notifications": {
        "task": "tasks.tasks.send_trimming_notifications",
        "schedule": crontab(),
        "args": (),
    },
    "send_seasonal_plant_notification": {
        "task": "tasks.tasks.send_seasonal_plant_notification",
        "schedule": crontab(hour=10, minute=0),
        "args": (),
    },
}

