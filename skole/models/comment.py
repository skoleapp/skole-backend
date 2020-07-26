from typing import TYPE_CHECKING, Optional, Union

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet

from skole.utils.validators import ValidateFileSizeAndType

from .base import SkoleManager, SkoleModel
from .course import Course
from .resource import Resource
from .user import User

if TYPE_CHECKING:  # pragma: no cover
    # To avoid circular import.
    from skole.utils.types import CommentableModel


class CommentManager(SkoleManager):
    def create_comment(
        self,
        user: User,
        text: str,
        attachment: Optional[UploadedFile],
        target: "CommentableModel",
    ) -> "Comment":
        if isinstance(target, Course):
            comment = self.model(course=target)
        elif isinstance(target, Resource):
            comment = self.model(resource=target)
        elif isinstance(target, Comment):
            comment = self.model(comment=target)
        else:
            raise TypeError(f"Invalid target type for Comment: {type(target)}")

        comment.user = user
        comment.text = text
        comment.attachment = attachment
        comment.save()
        return comment

    def update_comment(
        self, comment: "Comment", text: str, attachment: Union[UploadedFile, str],
    ) -> "Comment":
        comment.text = text
        comment.attachment = attachment
        comment.save()
        return comment

    def get_queryset(self) -> "QuerySet[Comment]":
        qs = super().get_queryset()
        return qs.annotate(score=Coalesce(Sum("votes__status"), Value(0)))


class Comment(SkoleModel):
    """Models one comment posted on a comment thread."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name="comments",
    )

    text = models.TextField(max_length=10000, blank=True)

    attachment = models.ImageField(
        upload_to="uploads/attachments",
        blank=True,
        validators=[
            ValidateFileSizeAndType(3, [("image/jpeg", "jpeg"), ("image/png", "png")])
        ],
    )

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=True, blank=True, related_name="comments"
    )

    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments",
    )

    comment = models.ForeignKey(
        "Comment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reply_comments",
    )

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    # Ignore: Mypy somehow thinks that this is incompatible with the super class.
    objects = CommentManager()  # type: ignore[assignment]

    # This value gets annotated in the manager's get_queryset.
    score: int

    def __str__(self) -> str:
        if self.text and len(self.text) > 40:
            return f"{self.text[:40]}..."
        elif self.text != "":
            return f"{self.text}"
        elif self.attachment != "":
            return f"Attachment Comment: {self.pk}"
        else:
            raise ValueError("Invalid comment with neither text nor attachment.")
