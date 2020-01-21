from django.db import models

from .resource_part_type import ResourcePartType


class ResourcePart(models.Model):
    """Models one user uploaded resource.

    TODO: Add a manager that requires at least an exercise number
     for a resource type of exercise and at least a title for
     other types of resource parts. Also prevent duplicate exercise numbers.
    """

    resource = models.ForeignKey(
        "Resource", on_delete=models.CASCADE, related_name="resource_parts"
    )
    resource_part_type = models.ForeignKey(
        ResourcePartType, on_delete=models.PROTECT, null=True
    )
    title = models.CharField(max_length=100)

    # TODO: Allow exercise numbers such as "4. b)" etc.
    #  maybe via char field or a separate field for sub exercise number?
    exercise_number = models.IntegerField(null=True)
    file = models.FileField(upload_to="uploads/resource_parts", null=True)
    text = models.TextField(max_length=1000, null=True)
