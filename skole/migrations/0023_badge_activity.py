# Generated by Django 3.1.7 on 2021-03-21 15:16

from __future__ import annotations

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0022_remove_redundant_fields_from_activities"),
    ]

    operations = [
        migrations.RenameField(
            model_name="activitytype",
            old_name="name",
            new_name="identifier",
        ),
        migrations.RemoveField(
            model_name="activity",
            name="target_user",
        ),
        migrations.AddField(
            model_name="activity",
            name="badge_progress",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="skole.badgeprogress",
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="causing_user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="caused_activities",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="new_badge_email_permission",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="user",
            name="new_badge_push_permission",
            field=models.BooleanField(default=True),
        ),
    ]
