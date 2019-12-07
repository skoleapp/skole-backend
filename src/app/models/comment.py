from django.db import models

from .resource import Resource
from .resource_part import ResourcePart
from .user import User
from .course import Course


class Comment(models.Model):
    """Models one comment, posted on a comment thread."""

    text = models.TextField(max_length=10000)
    attachment = models.FileField(upload_to="uploads/comment_attachments", null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="comments")
    
    # TODO: Add manager that allows only one foreign key.
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, related_name="comments")
    resource_part = models.ForeignKey(ResourcePart, on_delete=models.CASCADE, null=True, related_name="comments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, related_name="comments")

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        if len(self.text) > 20:
            return f"{self.creator.username}: {self.text[:20]}..."
        else:
            return f"{self.creator.username}: {self.text}"
