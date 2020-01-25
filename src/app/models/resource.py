from datetime import datetime
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
        date: Optional[datetime],
    ) -> "Resource":

        if not date:
            # If the user didn't provide a date for the resource, just use the current date.
            date = datetime.now()

        resource = self.model(
            resource_type=resource_type,
            title=title,
            course=course,
            user=user,
            date=date,
        )
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

    # The user can specify when the resource is dated.
    date = models.DateField(null=True)
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
