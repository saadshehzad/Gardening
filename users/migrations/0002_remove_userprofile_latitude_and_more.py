# Generated by Django 5.1.3 on 2025-06-26 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="latitude",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="longitude",
        ),
    ]
