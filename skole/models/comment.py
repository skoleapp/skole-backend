from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Value
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from skole.models.base import SkoleManager, SkoleModel
from skole.utils.constants import Notifications
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
        null=True,  # Null only for compatibility with old anonymous comments.
        blank=True,
    )

    is_anonymous = models.BooleanField(default=False)
    text = models.TextField(max_length=10000, blank=True)

    file = models.FileField(
        # This is the old path for the files in S3, will need to move them manually
        # when we want to update this.
        upload_to="uploads/resources",
        blank=True,
        max_length=500,
        validators=[
            ValidateFileSizeAndType(
                settings.FILE_MAX_SIZE,
                settings.FILE_ALLOWED_FILETYPES,
            )
        ],
    )

    image = models.ImageField(
        # This is the old path for the files in S3, will need to move them manually
        # when we want to update this.
        upload_to="uploads/attachments",
        blank=True,
        validators=[
            ValidateFileSizeAndType(
                settings.IMAGE_MAX_SIZE,
                settings.IMAGE_ALLOWED_FILETYPES,
            )
        ],
    )

    image_thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(100, 100)],
        format="JPEG",
        options={"quality": 60},
    )

    thread = models.ForeignKey(
        "skole.Thread",
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

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    # This value gets annotated in the manager's get_queryset.
    score: int

    def __str__(self) -> str:
        """This is only used implicitly in Django admin."""
        user = self.user.username if self.user else Notifications.COMMUNITY_USER

        if self.text and len(self.text) > 40:
            return f"{user}: {self.text[:40]}..."
        elif self.text != "":
            return f"{user}: {self.text}"
        elif self.image != "":
            return f"{user}: image comment: {self.pk}"
        elif self.file != "":
            return f"{user}: file comment: {self.pk}"
        else:
            raise ValueError("Invalid comment with neither text, image, nor file.")
