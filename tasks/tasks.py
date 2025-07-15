from celery import shared_task


@shared_task(name="tasks.abc")
def abc():
    print("Task1 is working.............")
