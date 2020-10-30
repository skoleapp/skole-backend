from typing import Optional

import graphene
from django.conf import settings
from django.db.models import Count, QuerySet
from graphene_django import DjangoObjectType

from skole.models import Subject
from skole.schemas.mixins import PaginationMixin
from skole.types import ID, ResolveInfo
from skole.utils import api_descriptions
from skole.utils.pagination import get_paginator


def order_subjects_by_num_courses(qs: QuerySet[Subject]) -> QuerySet[Subject]:
    """Sort the queryset so that the subjects with the most courses come first."""

    return qs.annotate(num_courses=Count("courses")).order_by(
        "-num_courses", "translations__name"
    )


class SubjectObjectType(DjangoObjectType):
    name = graphene.String()
    course_count = graphene.Int()
    resource_count = graphene.Int()

    class Meta:
        model = Subject
        description = api_descriptions.SUBJECT_OBJECT_TYPE
        fields = ("id", "name", "course_count", "resource_count")

    # Have to specify these three with resolvers since graphene cannot infer the annotated fields otherwise.

    @staticmethod
    def resolve_course_count(root: Subject, info: ResolveInfo) -> int:
        return root.course_count

    @staticmethod
    def resolve_resource_count(root: Subject, info: ResolveInfo) -> int:
        return root.resource_count


class PaginatedSubjectObjectType(PaginationMixin, graphene.ObjectType):
    objects = graphene.List(SubjectObjectType)

    class Meta:
        description = api_descriptions.PAGINATED_SUBJECT_OBJECT_TYPE


class Query(graphene.ObjectType):
    subjects = graphene.List(
        PaginatedSubjectObjectType,
        school=graphene.ID(),
        description=api_descriptions.SUBJECTS,
    )

    autocomplete_subjects = graphene.List(
        SubjectObjectType,
        name=graphene.String(),
        description=api_descriptions.AUTOCOMPLETE_SUBJECTS,
    )

    subject = graphene.Field(
        SubjectObjectType, id=graphene.ID(), description=api_descriptions.DETAIL_QUERY,
    )

    @staticmethod
    def resolve_subjects(
        root: None,
        info: ResolveInfo,
        school: ID = None,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> graphene.ObjectType:
        # Ignore: Mypy complains that `get(pk=None)` is not valid. It might not be
        # the most sensible thing, but it actually doesn't fail at runtime.
        qs: QuerySet[Subject] = Subject.objects.filter(courses__school__pk=school)  # type: ignore[misc]
        qs = order_subjects_by_num_courses(qs)
        return get_paginator(qs, page_size, page, PaginatedSubjectObjectType)

    @staticmethod
    def resolve_autocomplete_subjects(
        root: None, info: ResolveInfo, name: str = ""
    ) -> QuerySet[Subject]:
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
