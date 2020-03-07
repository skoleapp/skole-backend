from typing import Optional, Union

from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.db.models.query import QuerySet

from .course import Course
from .resource import Resource
from .user import User


class CommentManager(models.Manager):  # type: ignore[type-arg]
    def create_comment(
        self,
        user: User,
        text: str,
        attachment: Optional[UploadedFile],
        target: Union[Course, Resource, "Comment"],
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
        return qs.annotate(reply_count=models.Count("reply_comments")).order_by(
            "-reply_count", "id"
        )


class Comment(models.Model):
    """Models one comment posted on a comment thread."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="comments"
    )
    text = models.TextField(max_length=10000)
    attachment = models.FileField(upload_to="uploads/attachments", blank=True)

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
        if len(self.text) > 40:
            return f"{self.text[:40]}..."
        else:
            return f"{self.text}"
