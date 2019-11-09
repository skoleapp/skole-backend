from django.db import models

from .user import User


class ResourceComment(models.Model):
    """Models one comment posted on a resource."""
    text = models.TextField(max_length=10000)
    attachment = models.FileField(upload_to="uploads/comment_attachments", null=True)
    resource = models.ForeignKey("app.Resource", on_delete=models.CASCADE, related_name="resource_comments")

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_comments")

    points = models.IntegerField(default=0)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        if len(self.text) > 20:
            return f"{self.creator.username}: {self.text[:20]}..."
        else:
            return f"{self.creator.username}: {self.text}"
