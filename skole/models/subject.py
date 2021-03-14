from __future__ import annotations

from autoslug import AutoSlugField
from django.db import models
from django.db.models import Count
from django.db.models.query import QuerySet
from parler.models import TranslatedFields

from .base import TranslatableSkoleManager, TranslatableSkoleModel


class SubjectManager(TranslatableSkoleManager["Subject"]):
    def get_queryset(self) -> QuerySet[Subject]:
        qs = super().get_queryset()
        return qs.annotate(
            course_count=Count("courses", distinct=True),
            resource_count=Count("courses__resources", distinct=True),
        )


class Subject(TranslatableSkoleModel):
    """Models one studyable subject, e.g. Computer Engineering."""

    slug = AutoSlugField(
        null=True,
        default=None,
        populate_from="__str__",
        unique=True,
    )

    translations = TranslatedFields(name=models.CharField(max_length=100))

    objects = SubjectManager()

    # These values get annotated in the manager's get_queryset.
    course_count: int
    resource_count: int

    def __str__(self) -> str:
        return f"{self.name}"
