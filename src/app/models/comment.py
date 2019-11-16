from django.db import models

from app.models.comment_thread import CommentThread
from app.models.user import User


class Comment(models.Model):
    """Models one language, e.g. Finnish or English."""

    text = models.TextField(max_length=10000)
    attachment = models.FileField(upload_to="uploads/comment_attachments", null=True)
    comment_thread = models.ForeignKey(CommentThread, on_delete=models.CASCADE, related_name="reply_comments")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="comment_threads")

    points = models.IntegerField(default=0)

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        if len(self.text) > 20:
            return f"{self.creator.username}: {self.text[:20]}..."
        else:
            return f"{self.creator.username}: {self.text}"


