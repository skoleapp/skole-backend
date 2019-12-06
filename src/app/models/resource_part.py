from django.db import models

from .comment_thread import CommentThread
from .resource import Resource


class ResourcePart(models.Model):
    """Models one user uploaded resource."""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, related_name="resource_parts")
    comment_thread = models.OneToOneField(CommentThread, on_delete=models.CASCADE)
