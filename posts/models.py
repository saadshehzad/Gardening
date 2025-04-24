import uuid
from django.db import models
from users.models import User

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    description = models.TextField(max_length=100, null=True)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post {self.id}"

class UserPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s post"

class Articles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to="images/")
    url = models.CharField(max_length=1000)
    title = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ReportProblem(models.Model):
    image = models.TextField(null=True, blank=True)
    description = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Report by {self.user.username}"

class UserPostLike(models.Model):
    user_post = models.ForeignKey(UserPost, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.liked_by.username} liked"

class UserPostShare(models.Model):
    user_post = models.ForeignKey(UserPost, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.shared_by.username} shared"

class UserPostComment(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_post = models.ForeignKey(UserPost, on_delete=models.CASCADE)
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f"{self.comment_by.username} commented"