from __future__ import annotations

import datetime

from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Value
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet

from skole.utils.shortcuts import safe_annotation
from skole.utils.validators import ValidateFileSizeAndType

from .base import SkoleManager, SkoleModel


class ResourceManager(SkoleManager["Resource"]):
    def get_queryset(self) -> QuerySet[Resource]:
        qs = super().get_queryset()

        return qs.annotate(
            score=safe_annotation(qs, Coalesce(Sum("votes__status"), Value(0))),
            star_count=safe_annotation(qs, Count("stars", distinct=True)),
            comment_count=safe_annotation(
                qs,
                Count("comments", distinct=True)
                + Count("comments__reply_comments", distinct=True),
            ),
        )

    @staticmethod
    def increment_downloads(resource: Resource) -> Resource:
        resource.downloads += 1
        resource.save()
        return resource


class Resource(SkoleModel):
    """Models one user-uploaded resource."""

    slug = AutoSlugField(
        null=True,
        default=None,
        populate_from="__str__",
        unique_with=("title", "date"),
        always_update=True,
    )

    resource_type = models.ForeignKey("skole.ResourceType", on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    date = models.DateField(default=datetime.date.today, blank=True)

    file = models.FileField(
        upload_to="uploads/resources",
        blank=True,
        max_length=500,
        validators=[
            ValidateFileSizeAndType(
                settings.RESOURCE_FILE_MAX_SIZE,
                settings.RESOURCE_FILE_ALLOWED_FILETYPES,
            )
        ],
    )

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

    author = models.ForeignKey(
        "skole.Author",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="authored_resources",
        help_text="The author (=copyright owner) of the resource.",
    )

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ResourceManager()

    # These values get annotated in the manager's get_queryset.
    score: int
    star_count: int
    comment_count: int

    def __str__(self) -> str:
        return f"{self.title} {self.date}"
