from django.db import models

from .resource import Resource


class ResourcePartType(models.Model):
    """Models one type of resource resource part, e.g. an exercise or part of a note."""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return f"{self.name}"


class ResourcePart(models.Model):
    """Models one user uploaded resource.
    
    TODO: Add a manager that requires at least an exercise number
    for a resource type of exercise and at least a title for
    other types of resource parts. Also prevent duplicate exercise numbers."""


    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="resource_parts")
    resource_part_type = models.ForeignKey(ResourcePartType, on_delete=models.PROTECT)
    title = models.CharField(max_length=100, null=True)
   
    # TODO: Allow exercise numbers such as "4. b)" etc. maybe via char field or a separate field for sub exercise number?
    exercise_number = models.IntegerField(null=True)
    file = models.FileField(upload_to="uploads/resources", null=True)
    text = models.TextField(max_length=1000, null=True)
