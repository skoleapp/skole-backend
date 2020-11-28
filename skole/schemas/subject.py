from typing import Optional

import graphene
from django.conf import settings
from django.db.models import Count, QuerySet

from skole.models import Subject
from skole.schemas.base import SkoleDjangoObjectType, SkoleObjectType
from skole.schemas.mixins import PaginationMixin
from skole.types import ID, ResolveInfo
from skole.utils.pagination import get_paginator


def order_subjects_by_num_courses(qs: QuerySet[Subject]) -> QuerySet[Subject]:
    """Sort the queryset so that the subjects with the most courses come first."""

    return qs.annotate(num_courses=Count("courses")).order_by(
        "-num_courses", "translations__name"
    )


class SubjectObjectType(SkoleDjangoObjectType):
    name = graphene.String()
    course_count = graphene.Int()
    resource_count = graphene.Int()

    class Meta:
        model = Subject
        fields = ("id", "name", "course_count", "resource_count")

    # Have to specify these three with resolvers since graphene cannot infer the annotated fields otherwise.

    @staticmethod
    def resolve_course_count(root: Subject, info: ResolveInfo) -> int:
        return root.course_count

    @staticmethod
    def resolve_resource_count(root: Subject, info: ResolveInfo) -> int:
        return root.resource_count


class PaginatedSubjectObjectType(PaginationMixin, SkoleObjectType):
    objects = graphene.List(SubjectObjectType)

    class Meta:
        description = Subject.__doc__


class Query(SkoleObjectType):
    subjects = graphene.Field(
        PaginatedSubjectObjectType,
        school=graphene.ID(),
        page=graphene.Int(),
        page_size=graphene.Int(),
    )

    autocomplete_subjects = graphene.List(
        SubjectObjectType,
        name=graphene.String(),
    )

    subject = graphene.Field(SubjectObjectType, id=graphene.ID())

    @staticmethod
    def resolve_subjects(
        root: None,
        info: ResolveInfo,
        school: ID = None,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> PaginatedSubjectObjectType:
        """
        Filter results based on the school ID.

        Results are sorted by amount of courses.
        """
        qs: QuerySet[Subject] = Subject.objects.all()

        if school is not None:
            qs = qs.filter(courses__school__pk=school)

        qs = order_subjects_by_num_courses(qs)
        return get_paginator(qs, page_size, page, PaginatedSubjectObjectType)

    @staticmethod
    def resolve_autocomplete_subjects(
        root: None, info: ResolveInfo, name: str = ""
    ) -> QuerySet[Subject]:
        """Results are sorted by amount of courses."""
        qs = Subject.objects.translated()

        if name != "":
            qs = qs.filter(translations__name__icontains=name)

        qs = order_subjects_by_num_courses(qs)
        return qs[: settings.AUTOCOMPLETE_MAX_RESULTS]

    @staticmethod
    def resolve_subject(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[Subject]:
        return Subject.objects.get_or_none(pk=id)
