from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Count
from django.db.models.query import QuerySet
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from skole.models.base import SkoleManager, SkoleModel
from skole.utils.constants import Notifications
from skole.utils.files import generate_pdf_thumbnail
from skole.utils.validators import ValidateFileSizeAndType


class CommentManager(SkoleManager["Comment"]):
    def get_queryset(self) -> QuerySet[Comment]:
        qs = super().get_queryset()

        return qs.order_by(
            "id"  # We always want to get comments in their creation order.
        ).annotate(
            reply_count=Count("reply_comments", distinct=True),
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
    file_thumbnail = models.ImageField(
        upload_to="generated/thumbnails",
        blank=True,
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
        processors=[ResizeToFill(settings.THUMBNAIL_WIDTH, settings.THUMBNAIL_WIDTH)],
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

    score = models.IntegerField(default=0)

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    def __str__(self) -> str:
        """This is only used implicitly in Django admin."""
        user = self.user.username if self.user else Notifications.ANONYMOUS_STUDENT

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

    def change_score(self, score: int) -> None:
        if score:
            self.score += score  # Can also be a subtraction when `score` is negative.
            self.save(update_fields=("score",))

    def get_or_create_file_thumbnail_url(self) -> str:
        if not self.file:
            return ""
        if self.file_thumbnail:
            return self.file_thumbnail.url

        self.file_thumbnail = generate_pdf_thumbnail(self.file)
        self.save(update_fields=("file_thumbnail",))
        return self.file_thumbnail.url
