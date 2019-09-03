import datetime

from django.db import models

from .course import Course
from .user import User
from ..utils import RESOURCE_TYPES


class ResourceManager(models.Manager):
    def create_resource(self, user: User, title: str, file: str,
                        date: datetime.datetime) -> 'Resource':
        resource = self.model(
            title=title,
            file=file,
            date=date,
            creator=user,
        )
        resource.save()
        return resource


class Resource(models.Model):
    """Models one user uploaded resource."""
    resource_type = models.CharField(choices=RESOURCE_TYPES, max_length=10)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="uploads/resources")
    date = models.DateField(null=True, blank=True)  # The poster can specify when the resource is dated.
    points = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # TODO: custom deletor, which marks the user as some anonymous user
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ResourceManager()

    def __str__(self) -> str:
        return f"{self.title} by {self.creator.name}"
