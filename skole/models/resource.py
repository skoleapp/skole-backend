from __future__ import annotations

import datetime

from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Value
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet

from skole.utils.validators import ValidateFileSizeAndType

from .base import SkoleManager, SkoleModel


class ResourceManager(SkoleManager["Resource"]):
    def get_queryset(self) -> QuerySet[Resource]:
        qs = super().get_queryset()
        return qs.annotate(
            score=Coalesce(Sum("votes__status"), Value(0)),
            star_count=Count("stars", distinct=True),
            comment_count=Count("comments", distinct=True)
            + Count("comments__reply_comments", distinct=True),
        )

    @staticmethod
    def increment_downloads(resource: Resource) -> Resource:
        resource.downloads += 1
        resource.save()
        return resource


class Resource(SkoleModel):
    """Models one user-uploaded resource."""

    resource_type = models.ForeignKey("skole.ResourceType", on_delete=models.PROTECT)
    title = models.CharField(max_length=100)

    file = models.FileField(
        upload_to="uploads/resources",
        blank=True,
        max_length=500,
        validators=[ValidateFileSizeAndType(5, [("application/pdf", "PDF")])],
    )

    date = models.DateField(default=datetime.date.today, blank=True)

    course = models.ForeignKey(
        "skole.Course", on_delete=models.CASCADE, related_name="resources"
    )

    downloads = models.PositiveIntegerField(default=0)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_resources",
    )

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ResourceManager()

    # These values get annotated in the manager's get_queryset.
    score: int
    star_count: int
    comment_count: int

    def __str__(self) -> str:
        return f"{self.title}"
