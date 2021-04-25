from __future__ import annotations

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    """Remove courses that do not have resources or comments."""

    Course = apps.get_model("skole", "Course")
    Course.objects.filter(resources__isnull=True, comments__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0029_add_referral_code"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]
