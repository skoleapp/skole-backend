# Generated by Django 3.1.7 on 2021-03-26 08:11

from __future__ import annotations

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0026_update_users_email_notifications"),
    ]

    operations = [
        migrations.AddField(
            model_name="star",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="star",
            name="modified",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="vote",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="vote",
            name="modified",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
