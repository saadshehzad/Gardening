import uuid

from django.db import models

from users.models import User


class UserPost(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    image = models.ImageField(upload_to="images/",null=True,blank=True)
    description = models.TextField(max_length=100, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    time=models.DateTimeField(auto_now_add=True)


class Articles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to="images/")
    url = models.CharField(max_length=1000)
    title=models.CharField(max_length=255)
    user_name=models.CharField(max_length=255,)
    created_at=models.DateTimeField(auto_now_add=True)


class ReportProblem(models.Model):
    image = models.TextField(null=True,blank=True)
    description = models.CharField(max_length=100,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)


class UserPostLike(models.Model):
    user_post = models.ForeignKey(UserPost, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)


class UserPostShare(models.Model):
    user_post = models.ForeignKey(UserPost, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE)

class UserPostComment(models.Model):
    user_post = models.ForeignKey(UserPost, on_delete=models.CASCADE)
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE)