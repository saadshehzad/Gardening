# Generated by Django 5.1.3 on 2025-05-06 19:14

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userpostcomment",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
