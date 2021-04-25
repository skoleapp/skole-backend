# Generated by Django 3.1.7 on 2021-03-26 15:07
# Manually edited to add the `forwards_func`.
from __future__ import annotations

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    Badge = apps.get_model("skole", "Badge")
    Badge.objects.filter(identifier="first_resource").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0035_delete_resource_comment_activities"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]
