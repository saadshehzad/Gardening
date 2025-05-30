# Generated by Django 5.1.3 on 2025-04-29 16:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("posts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="reportproblem",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="userpost",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="posts.post"
            ),
        ),
        migrations.AddField(
            model_name="userpost",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="userpostcomment",
            name="comment_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="userpostcomment",
            name="user_post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="posts.userpost"
            ),
        ),
        migrations.AddField(
            model_name="userpostlike",
            name="liked_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="userpostlike",
            name="user_post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="posts.userpost"
            ),
        ),
        migrations.AddField(
            model_name="userpostshare",
            name="shared_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="userpostshare",
            name="user_post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="posts.userpost"
            ),
        ),
    ]
