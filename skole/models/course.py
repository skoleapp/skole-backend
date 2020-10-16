from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Count, F, QuerySet, Sum, Value
from django.db.models.functions import Coalesce

from .base import SkoleManager, SkoleModel


class CourseManager(SkoleManager["Course"]):
    def get_queryset(self) -> QuerySet[Course]:
        qs = super().get_queryset()
        return qs.annotate(
            score=Coalesce(Sum("votes__status", distinct=True), Value(0)),
            star_count=Count("stars", distinct=True),
            resource_count=Count("resources", distinct=True),
            top_level_comment_count=Count("comments", distinct=True),
            reply_comment_count=Count("comments__reply_comments", distinct=True),
            comment_count=F("top_level_comment_count") + F("reply_comment_count"),
        )


class Course(SkoleModel):
    """Models one course."""

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
