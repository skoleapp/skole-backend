from __future__ import annotations

from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.db.models import Count, QuerySet, Sum, Value
from django.db.models.functions import Coalesce
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from skole.models.base import SkoleManager, SkoleModel
from skole.utils.shortcuts import safe_annotation
from skole.utils.validators import ValidateFileSizeAndType


class ThreadManager(SkoleManager["Thread"]):
    def get_queryset(self) -> QuerySet[Thread]:
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


class Thread(SkoleModel):
    """Models one thread."""

    title = models.CharField(max_length=200)
    text = models.TextField(max_length=10000, blank=True)

    slug = AutoSlugField(
        null=True,
        default=None,
        populate_from="__str__",
        unique=True,
    )

    image = models.ImageField(
        upload_to="uploads/attachments",
        blank=True,
        validators=[
            ValidateFileSizeAndType(
                settings.COMMENT_ATTACHMENT_MAX_SIZE,
                settings.COMMENT_ATTACHMENT_ALLOWED_FILETYPES,
            )
        ],
    )

    image_thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(100, 100)],
        format="JPEG",
        options={"quality": 60},
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_threads",
    )

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    # These values will get annotated in the manager's get_queryset.
    score: int
    star_count: int
    resource_count: int
    comment_count: int

    def __str__(self) -> str:
        return f"{self.title}"
