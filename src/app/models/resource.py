from typing import Any

from django.db import models

from .course import Course
from .resource_part import ResourcePart
from .resource_type import ResourceType
from .user import User


class ResourceManager(models.Manager):
    def create_resource(
        self, resource_type: ResourceType, title: str, course: Course, files: Any
    ) -> "Resource":
        resource = self.model(resource_type=resource_type, title=title, course=course)
        resource.save()

        for file in files:
            """Automatically create resource parts based on amount of files provided."""

            title = f"File {file}"  # File 1, File 2...
            resource_part = ResourcePart.objects.create(
                resource=resource, title=title, file=file
            )
            resource_part.save()

        return resource


class Resource(models.Model):
    """Models one user-uploaded resource."""

    resource_type = models.ForeignKey(ResourceType, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    # The creator can specify when the resource is dated.
    # TODO: set to current date in the manager if not specified
    date = models.DateField(null=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="resources"
    )
    downloads = models.PositiveIntegerField(default=0, null=True)
    creator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_resources"
    )

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ResourceManager()

    def __str__(self) -> str:
        return f"'{self.title}' by {self.creator.username}"
