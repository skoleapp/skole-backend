# Generated by Django 3.1.5 on 2021-03-14 12:52
# Manually edited to add the `forwards_func`.
from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

import django.utils.translation
from django.apps.registry import Apps
from django.conf import settings
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

if TYPE_CHECKING:
    from skole.models import SkoleModel


@contextmanager
def dont_always_update_slug(model: type[SkoleModel]) -> Generator[None, None, None]:
    slug_field = model._meta.get_field("slug")  # pylint: disable=protected-access
    initial = slug_field.always_update
    slug_field.always_update = False
    try:
        yield
    finally:
        slug_field.always_update = initial


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    django.utils.translation.activate(settings.LANGUAGE_CODE)
    Course = apps.get_model("skole", "Course")

    with dont_always_update_slug(Course):
        for course in Course.objects.all():
            course.slug = None
            course.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0016_make_all_slugs_unique"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]
