from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Value
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from skole.models.base import SkoleManager, SkoleModel
from skole.utils.shortcuts import safe_annotation
from skole.utils.validators import ValidateFileSizeAndType


class CommentManager(SkoleManager["Comment"]):
    def get_queryset(self) -> QuerySet[Comment]:
        qs = super().get_queryset()

        return qs.order_by(
            "id"  # We always want to get comments in their creation order.
        ).annotate(
            score=safe_annotation(qs, Coalesce(Sum("votes__status"), Value(0))),
            reply_count=safe_annotation(qs, Count("reply_comments", distinct=True)),
        )


class Comment(SkoleModel):
    """Models one comment posted on a comment thread."""

    _identifier_field = "user"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="comments",
        null=True,
        blank=True,
    )

    text = models.TextField(max_length=10000, blank=True)

    attachment = models.ImageField(
        upload_to="uploads/attachments",
        blank=True,
        validators=[
            ValidateFileSizeAndType(
                settings.COMMENT_ATTACHMENT_MAX_SIZE,
                settings.COMMENT_ATTACHMENT_ALLOWED_FILETYPES,
            )
        ],
    )

    attachment_thumbnail = ImageSpecField(
        source="attachment",
        processors=[ResizeToFill(100, 100)],
        format="JPEG",
        options={"quality": 60},
    )

    course = models.ForeignKey(
        "skole.Course",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments",
    )

    resource = models.ForeignKey(
        "skole.Resource",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments",
    )

    comment = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reply_comments",
    )

    school = models.ForeignKey(
        "skole.School",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments",
    )

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    # This value gets annotated in the manager's get_queryset.
    score: int

    def __str__(self) -> str:
        """This is only used implicitly in Django admin."""
        user = self.user.username if self.user else "Community User"

        if self.text and len(self.text) > 40:
            return f"{user}: {self.text[:40]}..."
        elif self.text != "":
            return f"{user}: {self.text}"
        elif self.attachment != "":
            return f"{user}: attachment comment: {self.pk}"
        else:
            raise ValueError("Invalid comment with neither text nor attachment.")
