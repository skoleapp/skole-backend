from django.db import models
from django.db.models import Count, QuerySet
from parler.models import TranslatedFields

from skole.utils.shortcuts import safe_annotation

from .base import TranslatableSkoleManager, TranslatableSkoleModel
from .subject import Subject


class SchoolManager(TranslatableSkoleManager["School"]):
    def get_queryset(self) -> QuerySet["School"]:
        qs = super().get_queryset()

        return qs.annotate(
            comment_count=safe_annotation(
                qs,
                Count("comments", distinct=True)
                + Count("comments__reply_comments", distinct=True),
            ),
        )


class School(TranslatableSkoleModel):
    """Models one school on the platform."""

    school_type = models.ForeignKey(
        "skole.SchoolType", on_delete=models.PROTECT, related_name="schools"
    )

    city = models.ForeignKey(
        "skole.City", on_delete=models.PROTECT, related_name="schools"
    )

    translations = TranslatedFields(name=models.CharField(max_length=100))

    objects = SchoolManager()

    # These values will get annotated in the manager's get_queryset.
    comment_count: int

    def __str__(self) -> str:
        return f"{self.name}"

    @property
    def subjects(self) -> QuerySet[Subject]:
        return Subject.objects.filter(courses__in=self.courses.all()).distinct()
