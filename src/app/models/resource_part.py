from django.db import models


class ResourcePart(models.Model):
    """Models one user uploaded resource."""

    resource = models.ForeignKey(
        "Resource", on_delete=models.CASCADE, related_name="resource_parts"
    )
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="uploads/resource_parts", blank=True)
