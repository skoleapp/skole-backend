# Generated by Django 3.1.5 on 2021-02-17 22:12
# Manually edited to add the `forwards_func`.
from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator, Union

import django.utils.translation
from django.apps.registry import Apps
from django.conf import settings
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

if TYPE_CHECKING:  # pragma: no cover
    # Ignore: Some of the models do not exist anymore.
    from skole.models import (  # type: ignore[attr-defined]
        City,
        Country,
        Course,
        Resource,
        ResourceType,
        School,
        SchoolType,
        SkoleModel,
        Subject,
        User,
    )


def slug_course(self: Course) -> str:
    return f"{self.name} ({', '.join(self.codes)})" if self.codes else self.name


def slug_resource(self: Resource) -> str:
    return f"{self.title} {self.date}"


def slug_user(self: User) -> str:
    return self.username


def slug(self: Union[City, Country, ResourceType, School, SchoolType, Subject]) -> str:
    return self.name


@contextmanager
def dont_always_update_slug(model: type[SkoleModel]) -> Generator[None, None, None]:
    slug_field = model._meta.get_field("slug")
    initial = slug_field.always_update
    slug_field.always_update = False
    try:
        yield
    finally:
        slug_field.always_update = initial


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    django.utils.translation.activate(settings.LANGUAGE_CODE)

    for model_name, slug_func in (
        ("City", slug),
        ("Country", slug),
        ("ResourceType", slug),
        ("School", slug),
        ("SchoolType", slug),
        ("Subject", slug),
        ("Course", slug_course),
        ("Resource", slug_resource),
        ("User", slug_user),
    ):
        model = apps.get_model("skole", model_name)
        with dont_always_update_slug(model):
            for instance in model.objects.all():
                instance.slug = slug_func(instance)
                instance.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0009_add_product_update_and_blog_post_email_permissions"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]
