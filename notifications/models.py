from django.db import models

# class Notification(models.Model):
#     TYPE_ = (
#         ("Watering", "Watering")
#     )
#     type_ = models.CharField(max_length=50, choices=TYPE_)
#     mesage = models.TextField()
#     sent = models.BooleanField(default=False)



# @shared_task
# def sent_watering_notification():
#     users = User.objects.all()
#     for user in users:
#         Notification.objects.create()


