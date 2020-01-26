import datetime
from typing import List, Optional

from django.core.files.uploadedfile import UploadedFile
from django.db import models

from .course import Course
from .resource_part import ResourcePart
from .resource_type import ResourceType
from .user import User


class ResourceManager(models.Manager):
    def create_resource(
        self,
        resource_type: ResourceType,
        title: str,
        course: Course,
        files: List[UploadedFile],
        user: User,
        date: Optional[datetime.date] = None,
    ) -> "Resource":

        resource = self.model(
            resource_type=resource_type,
            title=title,
            course=course,
            user=user,
        )
        if date:
            # If the user did provide a date for the resource use that,
            # otherwise will just use the default from the model.
            resource.date = date
        resource.save()

        for file in files.values():
            # Automatically create resource parts based on amount of files provided.

            title = f"File {file}"  # File 1, File 2...
            resource_part = ResourcePart.objects.create(
                resource=resource, title=title, file=file
            )
            resource_part.save()

        return resource

    def update_resource(
        self,
        resource: "Resource",
        resource_type: ResourceType,
        title: str,
        date: datetime,
    ) -> "Resource":
        resource.resource_type = resource_type
        resource.title = title
        resource.date = date

        resource.save()
        return resource


class Resource(models.Model):
    """Models one user-uploaded resource."""

    resource_type = models.ForeignKey(ResourceType, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)

    date = models.DateField(default=datetime.date.today, blank=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="resources"
    )
    downloads = models.PositiveIntegerField(default=0, null=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_resources",
    )

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ResourceManager()

    def __str__(self) -> str:
        return f"'{self.title}' by {self.user.username}"
