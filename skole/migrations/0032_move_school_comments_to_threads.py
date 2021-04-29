from __future__ import annotations

from django.apps.registry import Apps
from django.conf import settings
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.utils import translation


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    """Create a thread for each school that has comments and move the comments there."""

    translation.activate(settings.LANGUAGE_CODE)
    School = apps.get_model("skole", "School")
    Thread = apps.get_model("skole", "Thread")

    for school in School.objects.filter(comments__isnull=False):
        thread = Thread.objects.create(title=school.name)
        school.comments.update(school=None, thread=thread)


class Migration(migrations.Migration):
    dependencies = [
        ("skole", "0031_rename_course_to_thread"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]
