from django.db import models

from .course import Course
from .user import User
from typing import Any


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


    resource = models.ForeignKey("Resource", on_delete=models.CASCADE, related_name="resource_parts")
    resource_part_type = models.ForeignKey(ResourcePartType, on_delete=models.PROTECT, null=True)
    title = models.CharField(max_length=100, null=True)
   
    # TODO: Allow exercise numbers such as "4. b)" etc. maybe via char field or a separate field for sub exercise number?
    exercise_number = models.IntegerField(null=True)
    file = models.FileField(upload_to="uploads/resources", null=True)
    text = models.TextField(max_length=1000, null=True)


class ResourceType(models.Model):
    """Models one type of resource, e.g. an exam or a note."""

    name = models.CharField(max_length=100, unique=True)
    has_parts = models.BooleanField()

    def __str__(self) -> str:
        return f"{self.name}"


class ResourceManager(models.Manager):
    def create_resource(self, resource_type: ResourceType, title: str, course: Course, files: [Any]) -> "Resource":
        resource = self.model(resource_type=resource_type, title=title, course=course)
        resource.save()

        for file in files:
            """Automatically create resource parts based on amount of files provided."""
            resource_part = ResourcePart.objects.create(resource=resource, file=file)
            resource_part.save()

        return resource


class Resource(models.Model):
    """Models one user-uploaded resource."""

    resource_type = models.ForeignKey(ResourceType, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    # The creator can specify when the resource is dated.
    # TODO: set to current date in the manager if not specified
    date = models.DateField(null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="resources")
    # TODO: custom deletor, which marks the user as some anonymous user
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_resources")

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ResourceManager()

    def __str__(self) -> str:
        return f"'{self.title}' by {self.creator.username}"
