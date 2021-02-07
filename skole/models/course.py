from __future__ import annotations

from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.db.models import Count, QuerySet, Sum, Value
from django.db.models.functions import Coalesce

from skole.utils.shortcuts import safe_annotation

from .base import SkoleManager, SkoleModel


class CourseManager(SkoleManager["Course"]):
    def get_queryset(self) -> QuerySet[Course]:
        qs = super().get_queryset()

        return qs.annotate(
            score=safe_annotation(qs, Coalesce(Sum("votes__status"), Value(0))),
            star_count=safe_annotation(qs, Count("stars", distinct=True)),
            resource_count=safe_annotation(qs, Count("resources", distinct=True)),
            comment_count=safe_annotation(
                qs,
                Count("comments", distinct=True)
                + Count("comments__reply_comments", distinct=True),
            ),
        )


class Course(SkoleModel):
    """Models one course."""

    slug = AutoSlugField(
        null=True,
        default=None,
        populate_from="__str__",
        unique_with=("name", "code"),
        always_update=True,
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, blank=True)

    subjects = models.ManyToManyField(
        "skole.Subject", related_name="courses", blank=True
    )

    school = models.ForeignKey(
        "skole.School", on_delete=models.CASCADE, related_name="courses"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_courses",
    )

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = CourseManager()

    # These values will get annotated in the manager's get_queryset.
    score: int
    star_count: int
    resource_count: int
    comment_count: int

    def __str__(self) -> str:
        return f"{self.name} {self.code}" if self.code else self.name
