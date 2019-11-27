from django.db import models

from .comment_thread import CommentThread
from .user import User
from .vote_holder import VoteHolder


class Comment(models.Model):
    """Models one comment, posted on a comment thread."""

    text = models.TextField(max_length=10000)
    attachment = models.FileField(upload_to="uploads/comment_attachments", null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="comments")
    comment_thread = models.ForeignKey(CommentThread, on_delete=models.CASCADE, related_name="comment_replies")

    vote_holder = models.OneToOneField(VoteHolder, on_delete=models.CASCADE, related_name="comment")

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        if len(self.text) > 20:
            return f"{self.creator.username}: {self.text[:20]}..."
        else:
            return f"{self.creator.username}: {self.text}"
