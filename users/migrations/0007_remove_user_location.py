# Generated by Django 5.1.3 on 2025-07-09 21:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_rename_address_user_location"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="location",
        ),
    ]
