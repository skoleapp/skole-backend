from django.db import models

from .comment_thread import CourseCommentThread, ResourceCommentThread
from .user import User


class Comment(models.Model):
    """Models one comment, posted on a comment thread."""

    text = models.TextField(max_length=10000)
    attachment = models.FileField(upload_to="uploads/comment_attachments", null=True)

    points = models.IntegerField(default=0)

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        if len(self.text) > 20:
            return f"{self.creator.username}: {self.text[:20]}..."
        else:
            return f"{self.creator.username}: {self.text}"


class ResourceComment(Comment):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="resource_comments")
    comment_thread = models.ForeignKey(ResourceCommentThread, on_delete=models.CASCADE, related_name="comment_replies")


class CourseComment(Comment):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="course_comments")
    comment_thread = models.ForeignKey(CourseCommentThread, on_delete=models.CASCADE, related_name="comment_replies")
