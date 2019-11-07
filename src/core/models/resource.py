from django.db import models

from .course import Course
from .user import User
from ..utils import RESOURCE_TYPES


class Resource(models.Model):
    """Models one user uploaded resource."""
    resource_type = models.CharField(choices=RESOURCE_TYPES, max_length=10)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="uploads/resources")
    date = models.DateField(null=True, blank=True)  # The poster can specify when the resource is dated.
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="resources")

    # TODO: custom deletor, which marks the user as some anonymous user
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="posted_resources")

    points = models.IntegerField(default=0)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"'{self.title}' by {self.poster.username}"
