# Generated by Django 3.2 on 2021-04-15 19:17

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0056_set_betauser_code_initial_usages"),
    ]

    operations = [
        migrations.AddField(
            model_name="thread",
            name="views",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="views",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
