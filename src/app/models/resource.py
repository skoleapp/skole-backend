from django.db import models

from .course import Course
from .user import User


class ResourceType(models.Model):
    """Models one type of resource, e.g. an exam or a note."""

    name = models.CharField(max_length=100, unique=True)
    has_parts = models.BooleanField()

    def __str__(self) -> str:
        return f"{self.name}"


class Resource(models.Model):
    """Models one user-uploaded resource."""

    resource_type = models.ForeignKey(ResourceType, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="uploads/resources")
    # The creator can specify when the resource is dated.
    # TODO: set to current date in the manager if not specified
    date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="resources")
    # TODO: custom deletor, which marks the user as some anonymous user
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_resources")

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"'{self.title}' by {self.creator.username}"
