import datetime
from typing import Optional

from django.conf import settings
from django.core.files import File
from django.db import models
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet

from skole.models.base import SkoleManager, SkoleModel
from skole.models.course import Course
from skole.models.resource_type import ResourceType
from skole.models.user import User
from skole.utils.validators import ValidateFileSizeAndType


class ResourceManager(SkoleManager):
    def create_resource(
        self,
        resource_type: ResourceType,
        title: str,
        course: Course,
        file: File,
        user: User,
        date: Optional[datetime.date] = None,
    ) -> "Resource":

        resource = self.model(
            resource_type=resource_type, title=title, course=course, user=user,
        )

        if date:
            # If the user did provide a date for the resource use that,
            # otherwise will just use the default from the model.
            resource.date = date

        resource.file = file
        resource.save()
        return resource

    def update_resource(
        self,
        resource: "Resource",
        resource_type: ResourceType,
        title: str,
        date: datetime.date,
    ) -> "Resource":
        resource.resource_type = resource_type
        resource.title = title
        resource.date = date
        resource.save()
        return resource

    def get_queryset(self) -> "QuerySet[Resource]":
        qs = super().get_queryset()
        return qs.annotate(score=Coalesce(Sum("votes__status"), Value(0)))


class Resource(SkoleModel):
    """Models one user-uploaded resource."""

    resource_type = models.ForeignKey("skole.ResourceType", on_delete=models.PROTECT)
    title = models.CharField(max_length=100)

    file = models.FileField(
        upload_to="uploads/resources",
        blank=True,
        max_length=500,
        validators=[ValidateFileSizeAndType(5, [("application/pdf", "PDF")])],
    )

    date = models.DateField(default=datetime.date.today, blank=True)

    course = models.ForeignKey(
        "skole.Course", on_delete=models.CASCADE, related_name="resources"
    )

    downloads = models.PositiveIntegerField(default=0)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_resources",
    )

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    # Ignore: Mypy somehow thinks that this is incompatible with the super class.
    objects = ResourceManager()  # type: ignore[assignment]

    # This value gets annotated in the manager's get_queryset.
    score: int

    def __str__(self) -> str:
        return f"{self.title}"
