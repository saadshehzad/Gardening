from celery import shared_task

@shared_task
def abc():
    print("Task1 is working.............")