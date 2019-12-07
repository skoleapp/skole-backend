from django.db import models

from .resource import Resource


class ResourcePart(models.Model):
    """Models one user uploaded resource."""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, related_name="resource_parts")
