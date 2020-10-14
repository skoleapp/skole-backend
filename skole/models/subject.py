from __future__ import annotations

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
            comment_count=Count("courses__resources__comments", distinct=True),
        )


class Subject(TranslatableSkoleModel):
    """Models one studyable subject, e.g. Computer Engineering."""

    translations = TranslatedFields(name=models.CharField(max_length=100))

    objects = SubjectManager()

    # This value gets annotated in the manager's get_queryset.
    course_count: int
    resource_count: int
    comment_count: int

    def __str__(self) -> str:
        return f"{self.name}"
