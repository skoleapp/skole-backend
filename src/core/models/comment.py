import datetime

from typing import Optional

from django.db import models

from .user import User


class CommentManager(models.Manager):
    def create_comment(self, user: User, text: str, attachment: Optional[str]) -> 'Comment':
        comment = self.model(
            text=text,
            attachment=attachment,
            creator=user,
        )
        comment.save()
        return comment


class Comment(models.Model):
    """Models one comment posted on a resource."""
    text = models.TextField(max_length=10000)
    attachment = models.FileField(upload_to="uploads/comment_attachments", null=True)
    points = models.IntegerField(default=0)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    def __str__(self) -> str:
        return f"{self.creator.username}: {self.text[:20]}"
