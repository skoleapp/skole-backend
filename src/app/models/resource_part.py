from django.db import models


class ResourceFile(models.Model):
    """Models one user uploaded resource."""

    resource = models.ForeignKey(
        "Resource", on_delete=models.CASCADE, related_name="resource_files"
    )
    file = models.FileField(upload_to="uploads/resource_parts", blank=True)
