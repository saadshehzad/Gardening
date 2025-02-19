import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.broker_url = 'redis://localhost:6379/0' 


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    
    
    
app.conf.beat_schedule = {
    "run-first-task":{
        "task": "tasks.tasks.abc",
        "schedule": crontab(minute="*/1"),
    }
}