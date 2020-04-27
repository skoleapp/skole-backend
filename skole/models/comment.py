from typing import TYPE_CHECKING, Optional, Union

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet

from skole.utils.validators import ValidateFileSizeAndType

from .course import Course
from .resource import Resource
from .user import User

if TYPE_CHECKING:
    # To avoid circular import.
    from skole.utils.types import CommentableModel


# Ignore: See explanation in UserManager.
class CommentManager(models.Manager):  # type: ignore[type-arg]
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
        comment.full_clean()
        comment.save()
        return comment

    def update_comment(
        self, comment: "Comment", text: str, attachment: Union[UploadedFile, str],
    ) -> "Comment":
        comment.text = text
        comment.attachment = attachment
        comment.full_clean()
        comment.save()
        return comment

    def get_queryset(self) -> "QuerySet[Comment]":
        return (
            super()
            .get_queryset()
            .annotate(reply_count=Count("reply_comments"))
            .order_by("-reply_count", "id")
        )


class Comment(models.Model):
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
        validators=[ValidateFileSizeAndType(3, ["image/jpeg", "image/png"])],
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

    objects = CommentManager()

    def __str__(self) -> str:
        if self.text and len(self.text) > 40:
            return f"{self.text[:40]}..."
        elif self.text != "":
            return f"{self.text}"
        elif self.attachment != "":
            return f"Attachment Comment: {self.pk}"
        else:
            raise ValueError("Invalid comment with neither text nor attachment.")

    @property
    def score(self) -> int:
        return self.votes.aggregate(score=Coalesce(Sum("status"), 0))["score"]