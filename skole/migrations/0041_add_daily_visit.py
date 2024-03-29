# Generated by Django 3.1.7 on 2021-03-27 12:01

from __future__ import annotations

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0040_add_attempted_email"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyVisit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("last_visit", models.DateTimeField(auto_now=True)),
                ("visits", models.PositiveIntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="daily_visits",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("date", "user")},
            },
        ),
    ]
