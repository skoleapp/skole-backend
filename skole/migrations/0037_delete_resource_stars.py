# Generated by Django 3.1.7 on 2021-03-26 22:10
# Manually edited to add the `forwards_func`.
from __future__ import annotations

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    Star = apps.get_model("skole", "Star")
    Star.objects.filter(resource__isnull=False).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0036_delete_first_resource_badge"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]
